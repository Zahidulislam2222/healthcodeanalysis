<?php
/**
 * Plugin Name: HC Design System Loader
 * Description: Must-use plugin that directly loads the HealthCode Design System.
 */

$design_plugin = WP_PLUGIN_DIR . '/healthcode-design-system/healthcode-design-system.php';
if (file_exists($design_plugin)) {
    require_once $design_plugin;
}
