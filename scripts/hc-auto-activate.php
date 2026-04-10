<?php
/**
 * Plugin Name: HC Design System Loader
 * Description: Must-use plugin — loads HealthCode Design System and sets security headers.
 */

// Security headers — set immediately at mu-plugin load (earliest possible point).
// HSTS omitted: Cloudflare handles it. PHP HSTS on cPanel causes redirect loops.
if (!headers_sent()) {
    header('X-Frame-Options: SAMEORIGIN');
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: strict-origin-when-cross-origin');
    header('Permissions-Policy: camera=(), microphone=(), geolocation=()');
    header("Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self'; frame-ancestors 'self';");
}

$design_plugin = WP_PLUGIN_DIR . '/healthcode-design-system/healthcode-design-system.php';
if (file_exists($design_plugin)) {
    require_once $design_plugin;
}
