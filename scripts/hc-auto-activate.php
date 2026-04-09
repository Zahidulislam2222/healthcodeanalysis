<?php
/**
 * Plugin Name: HC Auto-Activate
 * Description: Must-use plugin that ensures HealthCode Design System stays active.
 */

add_action('admin_init', function () {
    $plugin = 'healthcode-design-system/healthcode-design-system.php';
    if (!function_exists('is_plugin_active')) {
        require_once ABSPATH . 'wp-admin/includes/plugin.php';
    }
    if (!is_plugin_active($plugin) && file_exists(WP_PLUGIN_DIR . '/' . $plugin)) {
        activate_plugin($plugin);
    }
});
