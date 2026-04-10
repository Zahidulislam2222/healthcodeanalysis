#!/bin/bash
# cPanel Git deployment script — called by .cpanel.yml
# Uses $HOME (set by cPanel) instead of hardcoded username

WPROOT="$HOME/public_html/wp-content"

# API Bridge plugin
PLUGINDIR="$WPROOT/plugins/healthcode-api-bridge"
mkdir -p "$PLUGINDIR"
cp scripts/healthcode-api-bridge.php "$PLUGINDIR/healthcode-api-bridge.php"

# Design System plugin (dark theme + GSAP animations)
DESIGNDIR="$WPROOT/plugins/healthcode-design-system"
mkdir -p "$DESIGNDIR/css"
mkdir -p "$DESIGNDIR/js"
cp scripts/healthcode-design-system/healthcode-design-system.php "$DESIGNDIR/healthcode-design-system.php"
cp scripts/healthcode-design-system/css/healthcode-theme.css "$DESIGNDIR/css/healthcode-theme.css"
cp scripts/healthcode-design-system/js/healthcode-animations.js "$DESIGNDIR/js/healthcode-animations.js"

# Must-use plugin: auto-activates the design system
mkdir -p "$WPROOT/mu-plugins"
cp scripts/hc-auto-activate.php "$WPROOT/mu-plugins/hc-auto-activate.php"

echo "Deploy complete: plugins copied to $WPROOT"
