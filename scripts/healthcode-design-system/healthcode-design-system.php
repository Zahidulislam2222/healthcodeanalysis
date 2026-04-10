<?php
/**
 * Plugin Name: HealthCode Design System
 * Description: Dark glassmorphism theme with GSAP animations for a modern medical AI aesthetic.
 * Version: 3.0.0
 * Author: HealthCode Analysis
 * Requires PHP: 8.0
 */

defined('ABSPATH') || exit;

define('HC_DESIGN_VERSION', '3.4.0');
define('HC_DESIGN_PATH', plugin_dir_path(__FILE__));
define('HC_DESIGN_URL', plugin_dir_url(__FILE__));

/**
 * Enqueue all frontend assets: fonts, GSAP, theme CSS, animations JS.
 */
function hc_design_enqueue_assets(): void {
    // Google Fonts — Space Grotesk (headings) + Inter (body)
    wp_enqueue_style(
        'hc-google-fonts',
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap',
        [],
        null
    );

    // GSAP 3.12 core
    wp_enqueue_script(
        'gsap-core',
        'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js',
        [],
        '3.12.5',
        true
    );

    // GSAP ScrollTrigger plugin
    wp_enqueue_script(
        'gsap-scrolltrigger',
        'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js',
        ['gsap-core'],
        '3.12.5',
        true
    );

    // Theme CSS
    wp_enqueue_style(
        'hc-dark-theme',
        HC_DESIGN_URL . 'css/healthcode-theme.css',
        ['hc-google-fonts'],
        HC_DESIGN_VERSION
    );

    // Animations JS
    wp_enqueue_script(
        'hc-animations',
        HC_DESIGN_URL . 'js/healthcode-animations.js',
        ['gsap-core', 'gsap-scrolltrigger'],
        HC_DESIGN_VERSION,
        true
    );
}
add_action('wp_enqueue_scripts', 'hc_design_enqueue_assets');

/**
 * Exclude GSAP + animations from Cloudflare Rocket Loader.
 * Adds data-cfasync="false" so these scripts load normally while
 * Rocket Loader continues optimizing everything else.
 */
function hc_design_exclude_rocket_loader(string $tag, string $handle): string {
    $excluded = ['gsap-core', 'gsap-scrolltrigger', 'hc-animations'];
    if (in_array($handle, $excluded, true)) {
        $tag = str_replace('<script ', '<script data-cfasync="false" ', $tag);
    }

    // Subresource Integrity for external CDN scripts
    $sri_hashes = [
        'gsap-core'          => 'sha384-g4NTh/Iv5PPU4xPyhEWqPcwtNXOvdaDI8LLnyYfyNZOjKJeYQyjzQ9X5275eBjpt',
        'gsap-scrolltrigger' => 'sha384-Z3REaz79l2IaAZqJsSABtTbhjgOUYyV3p90XNnAPCSHg3EMTz1fouunq9WZRtj3d',
    ];
    if (isset($sri_hashes[$handle])) {
        $tag = str_replace(' src=', ' integrity="' . $sri_hashes[$handle] . '" crossorigin="anonymous" src=', $tag);
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
    echo '<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>' . "\n";
}
add_action('wp_head', 'hc_design_resource_hints', 1);

/**
 * Add theme-color meta for mobile browsers.
 */
function hc_design_theme_color(): void {
    echo '<meta name="theme-color" content="#0a0e1a">' . "\n";
}
add_action('wp_head', 'hc_design_theme_color', 2);
