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
    // CSP: each source verified from browser Console errors
    // unsafe-eval: MetForm template rendering
    // static.cloudflareinsights.com: Cloudflare Web Analytics beacon
    // www.google.com + www.gstatic.com: reCAPTCHA v3
    // font-src data:: inline base64 fonts from plugins
    // worker-src blob:: WordPress emoji detection worker
    // askme.healthcodeanalysis.workers.dev: AskMe chatbot Cloudflare Worker
    header("Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://static.cloudflareinsights.com https://www.google.com https://www.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https:; connect-src 'self' https://www.google.com https://askme.healthcodeanalysis.workers.dev; worker-src blob:; frame-src https://www.google.com; frame-ancestors 'self';");
}

$design_plugin = WP_PLUGIN_DIR . '/healthcode-design-system/healthcode-design-system.php';
if (file_exists($design_plugin)) {
    require_once $design_plugin;
}
