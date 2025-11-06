<?php
/**
 * Uninstall Script for Schema Validator Pro
 *
 * Fired when the plugin is uninstalled.
 *
 * @package Schema_Validator_Pro
 * @since 1.0.1
 */

// If uninstall not called from WordPress, exit
if (!defined('WP_UNINSTALL_PLUGIN')) {
    exit;
}

// Delete plugin options
delete_option('svp_api_endpoint');
delete_option('svp_api_key');
delete_option('svp_log_level');

// Delete all post meta created by the plugin
global $wpdb;

// Delete schema post meta
$wpdb->query("DELETE FROM {$wpdb->postmeta} WHERE meta_key LIKE '_svp_%'");

// Delete all transient cache
$wpdb->query(
    $wpdb->prepare(
        "DELETE FROM {$wpdb->options} WHERE option_name LIKE %s OR option_name LIKE %s",
        $wpdb->esc_like('_transient_svp_schema_') . '%',
        $wpdb->esc_like('_transient_timeout_svp_schema_') . '%'
    )
);

// Delete log files
$upload_dir = wp_upload_dir();
$log_dir = $upload_dir['basedir'] . '/schema-validator-pro-logs';

if (file_exists($log_dir)) {
    // Delete all log files
    $files = glob($log_dir . '/*');
    foreach ($files as $file) {
        if (is_file($file)) {
            unlink($file);
        }
    }
    
    // Remove directory
    rmdir($log_dir);
}

// Optional: Log uninstallation (if WP_DEBUG is enabled)
if (defined('WP_DEBUG') && WP_DEBUG) {
    error_log('[Schema Validator Pro] Plugin uninstalled and all data removed.');
}

