<?php
/** Search metadata and crawl eligibility for the actual native page content. */
if ( ! defined( 'ABSPATH' ) ) { exit; }
function hcn_policy() {
    static $policy;
    if ( null === $policy ) {
        $policy = json_decode( file_get_contents( __DIR__ . '/data/publishing-policy.json' ), true, 512, JSON_THROW_ON_ERROR );
    }
    return $policy;
}
function hcn_indexable( $id ) {
    return 'production' === wp_get_environment_type() && '1' === get_post_meta( $id, '_hcn_indexable', true );
}
function hcn_social_image( $image ) {
    $fallback = plugins_url( hcn_policy()['social_image'], __FILE__ );
    if ( ! is_string( $image ) || '' === trim( $image ) ) { return $fallback; }
    $image = trim( $image );
    if ( preg_match( '/[\x00-\x20\\\\]/', $image ) ) { return $fallback; }
    $parts = wp_parse_url( $image );
    if ( false === $parts || isset( $parts['user'] ) || isset( $parts['pass'] ) ) { return $fallback; }
    if ( ! isset( $parts['scheme'] ) && ! isset( $parts['host'] ) && '/' === substr( $image, 0, 1 ) && '//' !== substr( $image, 0, 2 ) ) {
        return home_url( $image );
    }
    $home = wp_parse_url( home_url( '/' ) );
    if ( ! isset( $parts['scheme'], $parts['host'] ) || ! in_array( $parts['scheme'], array( 'http', 'https' ), true ) ) { return $fallback; }
    $port = isset( $parts['port'] ) ? $parts['port'] : ( 'https' === $parts['scheme'] ? 443 : 80 );
    $home_port = isset( $home['port'] ) ? $home['port'] : ( 'https' === $home['scheme'] ? 443 : 80 );
    if ( $parts['scheme'] !== $home['scheme'] || strtolower( $parts['host'] ) !== strtolower( $home['host'] ) || $port !== $home_port ) { return $fallback; }
    return esc_url_raw( $image, array( 'http', 'https' ) );
}
add_filter( 'request', function ( $vars ) {
    if ( ! empty( $vars['category_name'] ) ) {
        $route = '/category/' . trim( $vars['category_name'], '/' ) . '/';
        $map = get_option( 'hcn_page_map', array() );
        if ( isset( $map[ $route ] ) ) { return array( 'page_id' => (int) $map[ $route ] ); }
    }
    return $vars;
} );
add_filter( 'wp_robots', function ( $robots ) {
    if ( ! is_singular() || ! hcn_indexable( get_queried_object_id() ) ) {
        $robots['noindex'] = true;
        unset( $robots['index'] );
    }
    $robots['max-image-preview'] = 'large';
    return $robots;
} );
add_action( 'init', function () { remove_action( 'wp_head', 'rel_canonical' ); } );
add_filter( 'document_title_parts', function ( $parts ) {
    if ( is_singular() ) { $parts['title'] = get_the_title(); }
    $parts['site'] = hcn_policy()['site_name'];
    return $parts;
} );
add_action( 'wp_head', function () {
    if ( ! is_singular() ) { return; }
    $id = get_queried_object_id(); $policy = hcn_policy();
    $url = get_permalink( $id );
    $title = wp_strip_all_tags( get_the_title( $id ) );
    $description = get_post_meta( $id, '_hcn_description', true );
    if ( ! $description ) { $description = $policy['site_description']; }
    $image = get_post_meta( $id, '_hcn_image', true );
    $image = hcn_social_image( $image );
    echo '<link rel="canonical" href="' . esc_url( $url ) . '">' . "\n";
    echo '<meta name="description" content="' . esc_attr( $description ) . '">' . "\n";
    $meta = array( 'og:type' => 'website', 'og:site_name' => $policy['site_name'], 'og:title' => $title, 'og:description' => $description, 'og:url' => $url, 'og:image' => $image, 'og:locale' => $policy['locale'] );
    foreach ( $meta as $key => $value ) { echo '<meta property="' . esc_attr( $key ) . '" content="' . esc_attr( $value ) . '">' . "\n"; }
    foreach ( array( 'twitter:card' => 'summary_large_image', 'twitter:title' => $title, 'twitter:description' => $description, 'twitter:image' => $image ) as $key => $value ) {
        echo '<meta name="' . esc_attr( $key ) . '" content="' . esc_attr( $value ) . '">' . "\n";
    }
    $site_id = home_url( '/#website' );
    $graph = array(
        array( '@type' => 'WebSite', '@id' => $site_id, 'url' => home_url( '/' ), 'name' => $policy['site_name'], 'description' => $policy['site_description'], 'inLanguage' => $policy['language'] ),
        array( '@type' => 'WebPage', '@id' => $url . '#webpage', 'url' => $url, 'name' => $title, 'description' => $description, 'isPartOf' => array( '@id' => $site_id ), 'inLanguage' => $policy['language'] ),
    );
    // No fictional ratings, clinician credentials, review dates or Article authors.
    echo '<script type="application/ld+json">' . wp_json_encode( array( '@context' => 'https://schema.org', '@graph' => $graph ), JSON_HEX_TAG | JSON_HEX_AMP ) . '</script>' . "\n";
}, 5 );
add_filter( 'wp_sitemaps_add_provider', function ( $provider, $name ) { return 'users' === $name || 'taxonomies' === $name ? false : $provider; }, 10, 2 );
add_filter( 'wp_sitemaps_post_types', function ( $types ) { return isset( $types['page'] ) ? array( 'page' => $types['page'] ) : array(); } );
add_filter( 'wp_sitemaps_posts_query_args', function ( $args ) {
    $args['meta_query'] = array( array( 'key' => '_hcn_indexable', 'value' => '1' ) );
    return $args;
} );
add_filter( 'robots_txt', function ( $text ) {
    if ( 'production' !== wp_get_environment_type() ) { return "User-agent: *\nDisallow: /\n"; }
    foreach ( hcn_policy()['training_agents_disallowed'] as $agent ) {
        $text .= "\nUser-agent: " . $agent . "\nDisallow: /\n";
    }
    return $text;
} );
add_action( 'template_redirect', function () {
    if ( ! is_page() ) { return; }
    $target = get_post_meta( get_queried_object_id(), '_hcn_redirect', true );
    if ( $target ) { wp_safe_redirect( home_url( $target ), 301 ); exit; }
} );
