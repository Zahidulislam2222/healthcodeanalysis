<?php
if ( ! defined( 'WP_CLI' ) || ! WP_CLI ) { exit; }
wp_set_current_user( 1 );
$data = json_decode( file_get_contents( '/import/pages.json' ), true );
$map = get_option( 'hcn_page_map', array() );
function hcn_store_layout( $id, $elements ) {
    update_post_meta( $id, '_elementor_edit_mode', 'builder' );
    update_post_meta( $id, '_elementor_template_type', 'wp-page' );
    update_post_meta( $id, '_elementor_version', ELEMENTOR_VERSION );
    update_post_meta( $id, '_elementor_data', wp_slash( wp_json_encode( $elements ) ) );
    update_post_meta( $id, '_elementor_page_settings', array( 'hide_title' => 'yes' ) );
    update_post_meta( $id, '_wp_page_template', 'elementor_header_footer' );
    \Elementor\Core\Files\CSS\Post::create( $id )->update();
}
foreach ( $data['pages'] as $page ) {
    $route = $page['route'];
    $parts = array_values( array_filter( explode( '/', $route ) ) );
    $slug = $parts ? end( $parts ) : 'home';
    $parent = 0;
    if ( count( $parts ) > 1 ) {
        $parent_path = implode( '/', array_slice( $parts, 0, -1 ) );
        $existing = get_page_by_path( $parent_path );
        $parent = $existing ? $existing->ID : wp_insert_post( array( 'post_title' => ucfirst( $parent_path ), 'post_name' => $parent_path, 'post_type' => 'page', 'post_status' => 'publish' ) );
    }
    $post = array( 'post_title' => $page['title'], 'post_name' => $slug, 'post_type' => 'page', 'post_status' => 'publish', 'post_parent' => $parent, 'post_content' => '' );
    if ( isset( $map[ $route ] ) ) { $post['ID'] = $map[ $route ]; }
    $id = wp_insert_post( $post, true );
    if ( is_wp_error( $id ) ) { WP_CLI::error( $id->get_error_message() ); }
    $map[ $route ] = $id;
    hcn_store_layout( $id, $page['elements'] );
    update_post_meta( $id, '_hcn_indexable', $page['indexable'] ? '1' : '0' );
    update_post_meta( $id, '_hcn_description', sanitize_text_field( $page['description'] ) );
    update_post_meta( $id, '_hcn_image', esc_url_raw( $page['image'] ) );
    update_post_meta( $id, '_hcn_redirect', $page['redirect'] );
}
update_option( 'hcn_page_map', $map );
update_option( 'show_on_front', 'page' ); update_option( 'page_on_front', $map['/'] );
foreach ( array( 'header', 'footer' ) as $type ) {
    $key = 'hcn_' . $type . '_id'; $id = get_option( $key );
    $post = array( 'post_title' => 'HealthCode ' . ucfirst( $type ), 'post_type' => 'elementor-hf', 'post_status' => 'publish' );
    if ( $id ) { $post['ID'] = $id; }
    $id = wp_insert_post( $post, true );
    if ( is_wp_error( $id ) ) { WP_CLI::error( $id->get_error_message() ); }
    update_option( $key, $id ); hcn_store_layout( $id, array( $data[ $type ] ) );
    update_post_meta( $id, 'ehf_template_type', 'type_' . $type );
    update_post_meta( $id, 'ehf_target_include_locations', array( 'rule' => array( 'basic-global' ), 'specific' => array() ) );
    update_post_meta( $id, 'display-on-canvas-template', '1' );
}
update_option( 'elementor_disable_color_schemes', 'yes' );
update_option( 'elementor_disable_typography_schemes', 'yes' );
update_option( 'elementor_experiment-container', 'active' );
update_option( 'permalink_structure', '/%postname%/' );
flush_rewrite_rules();
\Elementor\Plugin::$instance->files_manager->clear_cache();
WP_CLI::success( 'Imported ' . count( $map ) . ' native Elementor pages, free header and footer.' );
