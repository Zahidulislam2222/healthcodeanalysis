<?php
/**
 * Plugin Name: HealthCode API Bridge
 * Description: Exposes Elementor data and cache flush via REST API for automation scripts.
 * Version: 1.1.0
 * Author: HealthCode Analysis
 * Requires PHP: 8.0
 */

defined('ABSPATH') || exit;

/**
 * API Key authentication for HealthCode endpoints.
 * Falls back to standard WP auth (Application Passwords) if no API key provided.
 * Set the key in wp-config.php: define('HC_API_KEY', 'your-secret-key');
 * Or in the database via Settings > General (added by this plugin).
 */
function hc_check_api_auth(): bool {
    // Method 1: Check X-HC-API-Key header
    $api_key = $_SERVER['HTTP_X_HC_API_KEY'] ?? '';

    // Method 2: Check query parameter (fallback)
    if (empty($api_key)) {
        $api_key = $_GET['hc_api_key'] ?? '';
    }

    if (!empty($api_key)) {
        $stored_key = defined('HC_API_KEY') ? HC_API_KEY : get_option('hc_api_key', '');
        if (!empty($stored_key) && hash_equals($stored_key, $api_key)) {
            return true;
        }
    }

    // Method 3: Fall back to standard WordPress auth (Application Passwords)
    // Try manual Application Password validation for hosts where WP REST auth is broken
    if (!empty($_SERVER['PHP_AUTH_USER']) && !empty($_SERVER['PHP_AUTH_PW'])) {
        $user = get_user_by('login', sanitize_user($_SERVER['PHP_AUTH_USER']));
        if ($user) {
            $auth = wp_authenticate_application_password($user, $user->user_login, $_SERVER['PHP_AUTH_PW']);
            if (!is_wp_error($auth) && $auth instanceof WP_User) {
                wp_set_current_user($auth->ID);
                return true;
            }
        }
    }

    return current_user_can('edit_posts');
}

/**
 * Admin permission check (for cache flush).
 */
function hc_check_admin_auth(): bool {
    // API key auth grants admin access for our endpoints
    $api_key = $_SERVER['HTTP_X_HC_API_KEY'] ?? $_GET['hc_api_key'] ?? '';
    if (!empty($api_key)) {
        $stored_key = defined('HC_API_KEY') ? HC_API_KEY : get_option('hc_api_key', '');
        if (!empty($stored_key) && hash_equals($stored_key, $api_key)) {
            return true;
        }
    }

    // Manual Application Password check
    if (!empty($_SERVER['PHP_AUTH_USER']) && !empty($_SERVER['PHP_AUTH_PW'])) {
        $user = get_user_by('login', sanitize_user($_SERVER['PHP_AUTH_USER']));
        if ($user) {
            $auth = wp_authenticate_application_password($user, $user->user_login, $_SERVER['PHP_AUTH_PW']);
            if (!is_wp_error($auth) && $auth instanceof WP_User) {
                wp_set_current_user($auth->ID);
                return current_user_can('manage_options');
            }
        }
    }

    return current_user_can('manage_options');
}

add_action('rest_api_init', function () {

    // GET /wp-json/healthcode/v1/elementor-data/{post_id}
    register_rest_route('healthcode/v1', '/elementor-data/(?P<id>\d+)', [
        'methods'  => 'GET',
        'callback' => 'hc_get_elementor_data',
        'permission_callback' => 'hc_check_api_auth',
        'args' => [
            'id' => [
                'validate_callback' => function ($param) {
                    return is_numeric($param);
                },
            ],
        ],
    ]);

    // POST /wp-json/healthcode/v1/elementor-data/{post_id}
    register_rest_route('healthcode/v1', '/elementor-data/(?P<id>\d+)', [
        'methods'  => 'POST',
        'callback' => 'hc_update_elementor_data',
        'permission_callback' => 'hc_check_api_auth',
        'args' => [
            'id' => [
                'validate_callback' => function ($param) {
                    return is_numeric($param);
                },
            ],
        ],
    ]);

    // POST /wp-json/healthcode/v1/flush-elementor-cache
    register_rest_route('healthcode/v1', '/flush-elementor-cache', [
        'methods'  => 'POST',
        'callback' => 'hc_flush_elementor_cache',
        'permission_callback' => 'hc_check_admin_auth',
    ]);

    // GET /wp-json/healthcode/v1/page-map
    register_rest_route('healthcode/v1', '/page-map', [
        'methods'  => 'GET',
        'callback' => 'hc_get_page_map',
        'permission_callback' => 'hc_check_api_auth',
    ]);

    // POST /wp-json/healthcode/v1/rank-math-meta/{post_id}
    register_rest_route('healthcode/v1', '/rank-math-meta/(?P<id>\d+)', [
        'methods'  => 'POST',
        'callback' => 'hc_update_rank_math_meta',
        'permission_callback' => 'hc_check_api_auth',
        'args' => [
            'id' => [
                'validate_callback' => function ($param) {
                    return is_numeric($param);
                },
            ],
        ],
    ]);

    // POST /wp-json/healthcode/v1/upload-media
    register_rest_route('healthcode/v1', '/upload-media', [
        'methods'  => 'POST',
        'callback' => 'hc_upload_media',
        'permission_callback' => 'hc_check_api_auth',
    ]);

    // POST /wp-json/healthcode/v1/site-settings
    register_rest_route('healthcode/v1', '/site-settings', [
        'methods'  => 'POST',
        'callback' => 'hc_update_site_settings',
        'permission_callback' => 'hc_check_admin_auth',
    ]);

    // GET /wp-json/healthcode/v1/ping
    register_rest_route('healthcode/v1', '/ping', [
        'methods'  => 'GET',
        'callback' => function () {
            return new WP_REST_Response([
                'status'  => 'ok',
                'version' => '1.1.0',
                'site'    => get_bloginfo('name'),
                'url'     => home_url(),
            ], 200);
        },
        'permission_callback' => 'hc_check_api_auth',
    ]);
});

/**
 * Get Elementor data for a post.
 */
function hc_get_elementor_data(WP_REST_Request $request): WP_REST_Response {
    $post_id = (int) $request['id'];
    $post = get_post($post_id);

    if (!$post) {
        return new WP_REST_Response(['error' => 'Post not found'], 404);
    }

    $raw = get_post_meta($post_id, '_elementor_data', true);
    if (empty($raw)) {
        return new WP_REST_Response(['error' => 'No Elementor data for this post'], 404);
    }

    $data = json_decode($raw, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        return new WP_REST_Response(['error' => 'Invalid Elementor JSON'], 500);
    }

    return new WP_REST_Response([
        'post_id' => $post_id,
        'title'   => $post->post_title,
        'data'    => $data,
    ], 200);
}

/**
 * Update Elementor data for a post.
 */
function hc_update_elementor_data(WP_REST_Request $request): WP_REST_Response {
    $post_id = (int) $request['id'];
    $post = get_post($post_id);

    if (!$post) {
        return new WP_REST_Response(['error' => 'Post not found'], 404);
    }

    $body = $request->get_json_params();
    $new_data = $body['data'] ?? null;

    if (!$new_data || !is_array($new_data)) {
        return new WP_REST_Response(['error' => 'Missing or invalid "data" field'], 400);
    }

    $json = wp_json_encode($new_data);
    if (!$json) {
        return new WP_REST_Response(['error' => 'Failed to encode JSON'], 500);
    }

    update_post_meta($post_id, '_elementor_data', wp_slash($json));

    // Clear Elementor CSS cache for this post
    if (class_exists('\Elementor\Plugin')) {
        $css_file = \Elementor\Core\Files\CSS\Post::create($post_id);
        $css_file->delete();
    }

    return new WP_REST_Response([
        'success' => true,
        'post_id' => $post_id,
        'message' => 'Elementor data updated',
    ], 200);
}

/**
 * Flush Elementor CSS cache globally.
 */
function hc_flush_elementor_cache(): WP_REST_Response {
    $results = [];

    if (class_exists('\Elementor\Plugin')) {
        \Elementor\Plugin::$instance->files_manager->clear_cache();
        $results['elementor'] = 'Cache cleared';
    } else {
        $results['elementor'] = 'Elementor not active';
    }

    if (class_exists('LiteSpeed\Purge')) {
        \LiteSpeed\Purge::purge_all();
        $results['litespeed'] = 'Cache purged';
    } else {
        $results['litespeed'] = 'LiteSpeed not active';
    }

    return new WP_REST_Response([
        'success' => true,
        'results' => $results,
    ], 200);
}

/**
 * Get a map of all pages with Elementor data.
 */
function hc_get_page_map(): WP_REST_Response {
    global $wpdb;

    $results = $wpdb->get_results(
        "SELECT p.ID, p.post_title, p.post_status, p.post_type,
                LENGTH(pm.meta_value) as elementor_data_size
         FROM {$wpdb->posts} p
         INNER JOIN {$wpdb->postmeta} pm ON p.ID = pm.post_id AND pm.meta_key = '_elementor_data'
         WHERE p.post_status IN ('publish', 'draft')
           AND pm.meta_value != '[]'
           AND LENGTH(pm.meta_value) > 10
         ORDER BY p.post_type, p.post_title"
    );

    $pages = [];
    foreach ($results as $row) {
        $pages[] = [
            'id'          => (int) $row->ID,
            'title'       => $row->post_title,
            'status'      => $row->post_status,
            'type'        => $row->post_type,
            'data_size'   => (int) $row->elementor_data_size,
        ];
    }

    return new WP_REST_Response(['pages' => $pages], 200);
}

/**
 * Update Rank Math SEO meta for a post.
 */
function hc_update_rank_math_meta(WP_REST_Request $request): WP_REST_Response {
    $post_id = (int) $request['id'];
    $post = get_post($post_id);

    if (!$post) {
        return new WP_REST_Response(['error' => 'Post not found'], 404);
    }

    $body = $request->get_json_params();
    $allowed_keys = [
        'rank_math_title',
        'rank_math_description',
        'rank_math_focus_keyword',
        'rank_math_robots',
        'rank_math_facebook_title',
        'rank_math_facebook_description',
        'rank_math_facebook_image',
        'rank_math_twitter_title',
        'rank_math_twitter_description',
    ];

    $updated = [];
    foreach ($body as $key => $value) {
        if (in_array($key, $allowed_keys, true)) {
            update_post_meta($post_id, $key, sanitize_text_field($value));
            $updated[] = $key;
        }
    }

    return new WP_REST_Response([
        'success'      => true,
        'post_id'      => $post_id,
        'updated_keys' => $updated,
    ], 200);
}

/**
 * Upload media file.
 */
function hc_upload_media(WP_REST_Request $request): WP_REST_Response {
    require_once ABSPATH . 'wp-admin/includes/file.php';
    require_once ABSPATH . 'wp-admin/includes/image.php';
    require_once ABSPATH . 'wp-admin/includes/media.php';

    $files = $request->get_file_params();
    $file = $files['file'] ?? null;

    if (!$file) {
        return new WP_REST_Response(['error' => 'No file uploaded'], 400);
    }

    $upload = wp_handle_upload($file, ['test_form' => false]);

    if (isset($upload['error'])) {
        return new WP_REST_Response(['error' => $upload['error']], 500);
    }

    $attachment = [
        'post_title'     => sanitize_file_name(pathinfo($file['name'], PATHINFO_FILENAME)),
        'post_mime_type' => $upload['type'],
        'post_status'    => 'inherit',
    ];

    $attach_id = wp_insert_attachment($attachment, $upload['file']);
    $metadata = wp_generate_attachment_metadata($attach_id, $upload['file']);
    wp_update_attachment_metadata($attach_id, $metadata);

    // Set alt text if provided
    $alt = $request->get_param('alt_text');
    if ($alt) {
        update_post_meta($attach_id, '_wp_attachment_image_alt', sanitize_text_field($alt));
    }

    return new WP_REST_Response([
        'success' => true,
        'id'      => $attach_id,
        'url'     => wp_get_attachment_url($attach_id),
        'title'   => get_the_title($attach_id),
    ], 201);
}

/**
 * Update site settings (title, description, etc.).
 */
function hc_update_site_settings(WP_REST_Request $request): WP_REST_Response {
    $body = $request->get_json_params();
    $updated = [];

    $allowed = ['title' => 'blogname', 'description' => 'blogdescription'];

    foreach ($allowed as $key => $option_name) {
        if (isset($body[$key])) {
            update_option($option_name, sanitize_text_field($body[$key]));
            $updated[] = $key;
        }
    }

    // Handle site icon (favicon) by attachment ID
    if (isset($body['site_icon'])) {
        update_option('site_icon', (int) $body['site_icon']);
        $updated[] = 'site_icon';
    }

    // Handle custom logo by attachment ID
    if (isset($body['custom_logo'])) {
        set_theme_mod('custom_logo', (int) $body['custom_logo']);
        $updated[] = 'custom_logo';
    }

    return new WP_REST_Response([
        'success' => true,
        'updated' => $updated,
        'title'   => get_option('blogname'),
        'description' => get_option('blogdescription'),
    ], 200);
}
