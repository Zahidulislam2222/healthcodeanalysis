<?php
/** Small, scoped controls that preserve authenticated Elementor editing. */
if ( ! defined( 'ABSPATH' ) ) { exit; }
function hcn_script_hashes( $data = null ) {
    static $hashes = array();
    if ( null !== $data ) { $hashes[ "'sha256-" . base64_encode( hash( 'sha256', $data, true ) ) . "'" ] = true; }
    return array_keys( $hashes );
}
function hcn_public_cache_eligible() {
    foreach ( array( 'QUERY_STRING', 'HTTP_COOKIE', 'HTTP_AUTHORIZATION', 'REDIRECT_HTTP_AUTHORIZATION', 'REMOTE_USER' ) as $key ) {
        if ( isset( $_SERVER[ $key ] ) && '' !== (string) $_SERVER[ $key ] ) { return false; }
    }
    if ( is_user_logged_in() || ! is_singular() || post_password_required() ) { return false; }
    $path = wp_parse_url( get_permalink(), PHP_URL_PATH );
    return ! in_array( trailingslashit( $path ), hcn_policy()['excluded_routes'], true );
}
// Hash only scripts registered through WordPress, never arbitrary markup in content.
add_filter( 'wp_inline_script_attributes', function ( $attrs, $data ) {
    hcn_script_hashes( $data );
    return $attrs;
}, 10, 2 );
add_action( 'template_redirect', function () {
    if ( is_user_logged_in() || is_admin() ) { return; }
    ob_start( function ( $html ) {
        if ( headers_sent() ) { return $html; }
        $policy = hcn_policy();
        header( 'Content-Security-Policy: ' . str_replace( '{script_sources}', implode( ' ', hcn_script_hashes() ), $policy['security']['front_csp'] ) );
        $has_cookie_header = false;
        foreach ( headers_list() as $header ) { if ( 0 === stripos( $header, 'Set-Cookie:' ) ) { $has_cookie_header = true; } }
        $method = isset( $_SERVER['REQUEST_METHOD'] ) ? $_SERVER['REQUEST_METHOD'] : '';
        if ( $policy['delivery']['cache_anonymous_html'] && in_array( $method, array( 'GET', 'HEAD' ), true ) &&
             empty( $_GET ) && empty( $_COOKIE ) && ! $has_cookie_header && 200 === http_response_code() &&
             hcn_public_cache_eligible() ) {
            header( 'Cache-Control: public, max-age=0, s-maxage=' . (int) $policy['delivery']['public_cache_seconds'] .
                ', stale-while-revalidate=' . (int) $policy['delivery']['stale_while_revalidate_seconds'] . ', no-transform' );
        }
        return $html;
    } );
}, 1 );
add_action( 'send_headers', function () {
    $security = hcn_policy()['security'];
    header_remove( 'X-Powered-By' );
    header( 'X-Content-Type-Options: nosniff' );
    header( 'Referrer-Policy: ' . $security['referrer_policy'] );
    header( 'Permissions-Policy: ' . $security['permissions_policy'] );
    header( 'X-Frame-Options: SAMEORIGIN' );
    // Private by default; only verified anonymous HTML is made cacheable at render completion.
    header( 'Cache-Control: private, no-store, no-transform' );
    if ( ! is_user_logged_in() && ! is_admin() ) {
        header( 'Content-Security-Policy: ' . str_replace( '{script_sources}', '', $security['front_csp'] ) );
    }
    if ( is_ssl() && 'production' === wp_get_environment_type() ) {
        header( 'Strict-Transport-Security: max-age=' . (int) $security['hsts_seconds'] );
    }
} );
add_filter( 'xmlrpc_enabled', '__return_false' );
add_filter( 'wp_is_application_passwords_available', '__return_false' );
add_filter( 'comments_open', '__return_false', 20 );
add_filter( 'pings_open', '__return_false', 20 );
add_filter( 'the_generator', '__return_empty_string' );
add_action( 'init', function () {
    remove_action( 'wp_head', 'rsd_link' );
    remove_action( 'wp_head', 'wlwmanifest_link' );
    remove_action( 'wp_head', 'wp_generator' );
    if ( defined( 'XMLRPC_REQUEST' ) && XMLRPC_REQUEST ) { status_header( 403 ); exit; }
} );
add_filter( 'rest_pre_dispatch', function ( $result, $server, $request ) {
    if ( ! is_user_logged_in() && preg_match( '#^/wp/v2/users(?:/|$)#', $request->get_route() ) ) {
        return new WP_Error( 'hcn_private_resource', 'Authentication required.', array( 'status' => 401 ) );
    }
    return $result;
}, 10, 3 );
add_action( 'template_redirect', function () {
    if ( is_author() ) { global $wp_query; $wp_query->set_404(); status_header( 404 ); }
}, 0 );
add_filter( 'login_errors', function () { return esc_html__( 'Sign-in failed. Check your credentials and try again.', 'healthcode-native' ); } );
