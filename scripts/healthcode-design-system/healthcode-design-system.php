<?php
/**
 * Plugin Name: HealthCode Design System
 * Description: Dark glassmorphism theme with GSAP animations for a modern medical AI aesthetic.
 * Version: 3.0.0
 * Author: HealthCode Analysis
 * Requires PHP: 8.0
 */

defined('ABSPATH') || exit;

define('HC_DESIGN_VERSION', '3.6.0');
define('HC_DESIGN_PATH', plugin_dir_path(__FILE__));
define('HC_DESIGN_URL', plugin_dir_url(__FILE__));

/**
 * Enqueue all frontend assets: fonts, theme CSS, animations JS.
 * No external animation libraries — uses vanilla IntersectionObserver + CSS transitions.
 */
function hc_design_enqueue_assets(): void {
    // Google Fonts — Space Grotesk (headings) + Inter (body)
    wp_enqueue_style(
        'hc-google-fonts',
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap',
        [],
        null
    );

    // Theme CSS
    wp_enqueue_style(
        'hc-dark-theme',
        HC_DESIGN_URL . 'css/healthcode-theme.css',
        ['hc-google-fonts'],
        HC_DESIGN_VERSION
    );

    // Animations JS (vanilla — no dependencies)
    wp_enqueue_script(
        'hc-animations',
        HC_DESIGN_URL . 'js/healthcode-animations.js',
        [],
        HC_DESIGN_VERSION,
        true
    );
}
add_action('wp_enqueue_scripts', 'hc_design_enqueue_assets');

/**
 * Exclude animations JS from Cloudflare Rocket Loader.
 * Adds data-cfasync="false" so animations load normally.
 */
function hc_design_exclude_rocket_loader(string $tag, string $handle): string {
    if ($handle === 'hc-animations') {
        $tag = str_replace('<script ', '<script data-cfasync="false" ', $tag);
    }
    return $tag;
}
add_filter('script_loader_tag', 'hc_design_exclude_rocket_loader', 10, 2);

/**
 * Add dark-theme class to <body> on the frontend.
 */
function hc_design_body_class(array $classes): array {
    if (!is_admin()) {
        $classes[] = 'hc-dark-theme';
    }
    return $classes;
}
add_filter('body_class', 'hc_design_body_class');

/**
 * Preconnect to Google Fonts and CDNJS for faster loading.
 */
function hc_design_resource_hints(): void {
    echo '<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>' . "\n";
    echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' . "\n";
}
add_action('wp_head', 'hc_design_resource_hints', 1);

/**
 * Add theme-color meta for mobile browsers.
 */
function hc_design_theme_color(): void {
    echo '<meta name="theme-color" content="#0a0e1a">' . "\n";
}
add_action('wp_head', 'hc_design_theme_color', 2);
