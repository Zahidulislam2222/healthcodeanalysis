#!/bin/bash
# ============================================================
# HealthCode Analysis — Local Docker Setup
# ============================================================
# This script:
# 1. Starts Docker containers (WordPress + MySQL + phpMyAdmin)
# 2. Waits for WordPress to be ready
# 3. Installs WP-CLI
# 4. Installs required plugins (Elementor, ACF, Rank Math, etc.)
# 5. Installs All-in-One WP Migration for .wpress import
# 6. Activates the HealthCode API Bridge plugin
# 7. Sets up the HC_API_KEY for local testing
#
# After running this script:
# - WordPress: http://localhost:8889
# - WP Admin:  http://localhost:8889/wp-admin (admin / admin)
# - phpMyAdmin: http://localhost:8082
# - GraphQL:   N/A (not needed for this project)
#
# To import the .wpress file:
# 1. Go to http://localhost:8889/wp-admin
# 2. Plugins > All-in-One WP Migration > Import
# 3. Upload the .wpress file
# 4. Login again with the LIVE site credentials after import
# ============================================================

set -e

echo "=== Starting Docker containers ==="
docker-compose up -d

echo ""
echo "=== Waiting for WordPress to be ready ==="
MAX_WAIT=120
ELAPSED=0
until docker exec hc-wordpress curl -sf http://localhost:80 > /dev/null 2>&1; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    if [ $ELAPSED -ge $MAX_WAIT ]; then
        echo "ERROR: WordPress did not start within ${MAX_WAIT}s"
        exit 1
    fi
    echo "  Waiting... (${ELAPSED}s)"
done
echo "  WordPress is up!"

echo ""
echo "=== Installing WP-CLI ==="
docker exec hc-wordpress bash -c '
    if ! command -v wp &> /dev/null; then
        curl -sO https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
        chmod +x wp-cli.phar
        mv wp-cli.phar /usr/local/bin/wp
    fi
    wp --info --allow-root 2>/dev/null | head -3
'

echo ""
echo "=== Completing WordPress installation ==="
docker exec hc-wordpress wp core install \
    --url="http://localhost:8889" \
    --title="HealthCode Analysis (Local)" \
    --admin_user=admin \
    --admin_password=admin \
    --admin_email=admin@localhost.local \
    --skip-email \
    --allow-root 2>/dev/null || echo "  (Already installed)"

echo ""
echo "=== Installing plugins ==="
PLUGINS=(
    "elementor"
    "advanced-custom-fields"
    "seo-by-rank-math"
    "jeg-elementor-kit"
    "royal-elementor-addons"
    "metform"
    "all-in-one-wp-migration"
    "code-snippets"
    "duplicate-post"
)

for plugin in "${PLUGINS[@]}"; do
    echo "  Installing: $plugin"
    docker exec hc-wordpress wp plugin install "$plugin" --activate --allow-root 2>/dev/null || \
        echo "    (already installed or unavailable)"
done

echo ""
echo "=== Activating HealthCode API Bridge ==="
docker exec hc-wordpress wp plugin activate healthcode-api-bridge --allow-root 2>/dev/null || \
    echo "  (already active or not found)"

echo ""
echo "=== Setting up HC_API_KEY ==="
# Use the same API key as .env for consistency
HC_KEY=$(grep HC_API_KEY ../.env 2>/dev/null | cut -d= -f2 | tr -d ' "')
if [ -n "$HC_KEY" ]; then
    docker exec hc-wordpress wp config set HC_API_KEY "$HC_KEY" --raw --type=constant --allow-root 2>/dev/null || true
    echo "  API key set from .env"
else
    # Generate a new one
    HC_KEY=$(openssl rand -base64 32 | tr -d '/+=' | head -c 32)
    docker exec hc-wordpress wp config set HC_API_KEY "$HC_KEY" --raw --type=constant --allow-root 2>/dev/null || true
    echo "  Generated new API key: $HC_KEY"
fi

echo ""
echo "=== Setting Astra theme ==="
docker exec hc-wordpress wp theme install astra --activate --allow-root 2>/dev/null || \
    echo "  (already installed)"

echo ""
echo "=== Creating Application Password ==="
docker exec hc-wordpress wp user application-password create admin "local-automation" --porcelain --allow-root 2>/dev/null || \
    echo "  (already exists or not supported)"

echo ""
echo "=== Increasing upload size ==="
docker exec hc-wordpress bash -c '
    echo "upload_max_filesize = 512M" > /usr/local/etc/php/conf.d/uploads.ini
    echo "post_max_size = 512M" >> /usr/local/etc/php/conf.d/uploads.ini
    echo "memory_limit = 512M" >> /usr/local/etc/php/conf.d/uploads.ini
    echo "max_execution_time = 300" >> /usr/local/etc/php/conf.d/uploads.ini
    echo "max_input_time = 300" >> /usr/local/etc/php/conf.d/uploads.ini
'

echo ""
echo "=== Restarting Apache for PHP changes ==="
docker exec hc-wordpress apache2ctl graceful 2>/dev/null || true

echo ""
echo "============================================================"
echo "  LOCAL WORDPRESS READY"
echo "============================================================"
echo ""
echo "  WordPress:  http://localhost:8889"
echo "  WP Admin:   http://localhost:8889/wp-admin"
echo "  Login:      admin / admin"
echo "  phpMyAdmin: http://localhost:8082"
echo ""
echo "  NEXT STEP: Import the .wpress file"
echo "  Go to WP Admin > All-in-One WP Migration > Import"
echo "  Upload: healthcodeanalysis-com-*.wpress"
echo ""
echo "  After import, login with the LIVE site credentials:"
echo "  Username: hcanalysis"
echo "============================================================"
