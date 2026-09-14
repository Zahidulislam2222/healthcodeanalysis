<?php
/**
 * Plugin Name: HealthCode Native Design
 * Description: Design tokens and browser tools for native Elementor Free content.
 * Version: 1.0.0
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

require_once __DIR__ . '/publishing.php';
require_once __DIR__ . '/security.php';
require_once __DIR__ . '/library-controls.php';

function hcn_data( $name ) {
    $allowed = array( 'site', 'config', 'tools', 'editor-fields' );
    if ( ! in_array( $name, $allowed, true ) ) { return array(); }
    return json_decode( file_get_contents( __DIR__ . '/data/' . $name . '.json' ), true );
}
add_action( 'acf/init', function () {
    if ( function_exists( 'acf_add_local_field_group' ) ) {
        acf_add_local_field_group( hcn_data( 'editor-fields' ) );
    }
} );
add_filter( 'elementor/frontend/print_google_fonts', '__return_false' );
add_filter( 'body_class', function ( $classes ) {
    $classes[] = 'hc-native';
    if ( is_front_page() ) { $classes[] = 'home-page'; }
    return $classes;
} );
add_action( 'wp_enqueue_scripts', function () {
    $url = plugin_dir_url( __FILE__ );
    foreach ( array( 'native-base', 'fonts', 'tokens', 'main', 'frontier' ) as $style ) {
        wp_enqueue_style( 'hcn-' . $style, $url . 'assets/styles/' . $style . '.css', array(), filemtime( __DIR__ . '/assets/styles/' . $style . '.css' ) );
    }
    if ( is_front_page() ) { wp_enqueue_style( 'hcn-hero', $url . 'assets/styles/hero.css', array(), filemtime( __DIR__ . '/assets/styles/hero.css' ) ); }
    wp_enqueue_style( 'hcn-adapter', $url . 'assets/styles/native-adapter.css', array(), filemtime( __DIR__ . '/assets/styles/native-adapter.css' ) );
    wp_enqueue_script( 'hcn-app', $url . 'assets/scripts/app.mjs', array(), filemtime( __DIR__ . '/assets/scripts/app.mjs' ), true );
}, 99 );
add_filter( 'script_loader_tag', function ( $tag, $handle ) {
    if ( 'hcn-app' === $handle ) { return str_replace( '<script ', '<script type="module" ', $tag ); }
    return $tag;
}, 10, 2 );

// Preserve semantic attributes used by the local tools on native widgets.
function hcn_attributes( $element ) {
    $settings = $element->get_data( 'settings' );
    $attrs = isset( $settings['hc_attributes'] ) ? $settings['hc_attributes'] : array();
    return is_array( $attrs ) ? $attrs : array();
}
add_action( 'elementor/frontend/container/before_render', function ( $element ) {
    foreach ( hcn_attributes( $element ) as $key => $value ) {
        if ( 'tabindex' === $key && in_array( (string) $value, array( '-1', '0' ), true ) ) {
            $element->add_render_attribute( '_wrapper', $key, $value );
        }
        if ( preg_match( '/^(data-[a-z0-9-]+|aria-[a-z0-9-]+|role|hidden)$/', $key ) ) {
            $element->add_render_attribute( '_wrapper', 'data-id' === $key ? 'data-story-id' : $key, $value );
        }
    }
} );
add_filter( 'elementor/widget/render_content', function ( $html, $widget ) {
    $attrs = hcn_attributes( $widget );
    $raw = $widget->get_data( 'settings' );
    if ( 'button' === $widget->get_name() && ! empty( $raw['hc_icon'] ) ) {
        $icon = '<img class="hc-inline-icon" src="' . esc_url( $raw['hc_icon'] ) . '" alt="">';
        $html = str_replace( '</a>', $icon . '</a>', $html );
    }
    if ( ! empty( $raw['hc_save_label'] ) ) {
        $label = new WP_HTML_Tag_Processor( $html );
        if ( $label->next_tag( array( 'class_name' => 'elementor-button-text' ) ) ) { $label->set_attribute( 'data-save-label', '' ); }
        $html = $label->get_updated_html();
    }
    if ( ! empty( $raw['hc_saved_count'] ) ) { $html = str_replace( '</a>', '<span data-saved-count hidden></span></a>', $html ); }
    if ( ! $attrs ) { return $html; }
    $processor = new WP_HTML_Tag_Processor( $html );
    $target = 'button' === $widget->get_name() ? 'A' : ( 'image' === $widget->get_name() ? 'IMG' : null );
    if ( $processor->next_tag( $target ) ) {
        foreach ( $attrs as $key => $value ) {
            if ( preg_match( '/^(class|id|title|alt|role|data-[a-z0-9-]+|aria-[a-z0-9-]+)$/', $key ) ) {
                if ( 'class' === $key ) { $processor->add_class( $value ); }
                else { $processor->set_attribute( $key, $value ); }
            }
        }
        $html = $processor->get_updated_html();
    }
    if ( 'button' === $widget->get_name() && isset( $attrs['data-hc-button'] ) ) {
        $html = preg_replace( '/<a\b/', '<button type="button"', $html, 1 );
        $html = preg_replace( '/<\/a>/', '</button>', $html, 1 );
    }
    return $html;
}, 10, 2 );

add_action( 'wp_footer', function () {
    $site = hcn_data( 'site' ); $config = hcn_data( 'config' );
    $config['search_index'] = plugins_url( 'assets/library-index.json', __FILE__ );
    $config['frontier']['video_url'] = plugins_url( 'assets/neural-film.mp4', __FILE__ );
    echo '<script type="application/json" id="frontend-config">' . wp_json_encode( array( 'client' => $config, 'labels' => $site['labels'], 'tools' => hcn_data( 'tools' ) ), JSON_HEX_TAG | JSON_HEX_AMP ) . '</script>';
    // Trusted, locally generated application-dialog template; never accepts request content.
    require __DIR__ . '/templates/dialogs.php';
}, 5 );
add_shortcode( 'healthcode_tool', function ( $attrs ) {
    $attrs = shortcode_atts( array( 'id' => '' ), $attrs );
    $tools = hcn_data( 'tools' );
    if ( ! isset( $tools[ $attrs['id'] ] ) ) { return ''; }
    ob_start(); require __DIR__ . '/templates/tool-' . sanitize_key( $attrs['id'] ) . '.php'; return ob_get_clean();
} );
