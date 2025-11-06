<?php
/**
 * Plugin Name: Schema Validator Pro
 * Description: Automatically inject Schema.org JSON-LD markup into WordPress posts and pages
 * Version: 1.0.1
 * Author: Schema Validator Pro Team
 * Text Domain: schema-validator-pro
 * Domain Path: /languages
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

// Plugin constants
define('SCHEMA_VALIDATOR_PRO_VERSION', '1.0.1');
define('SCHEMA_VALIDATOR_PRO_FILE', __FILE__);
define('SCHEMA_VALIDATOR_PRO_DIR', plugin_dir_path(__FILE__));
define('SCHEMA_VALIDATOR_PRO_URL', plugin_dir_url(__FILE__));

// Load logger class
require_once SCHEMA_VALIDATOR_PRO_DIR . 'includes/class-logger.php';

/**
 * Helper function to escape LIKE wildcards for wpdb
 * Provides compatibility with older WordPress versions
 */
function svp_esc_like($text) {
    global $wpdb;

    // Use wpdb::esc_like() if available (WordPress 4.0+)
    if (method_exists($wpdb, 'esc_like')) {
        return $wpdb->esc_like($text);
    }

    // Fallback for older versions
    return addcslashes($text, '_%\\');
}

/**
 * Load plugin textdomain for i18n
 */
function svp_load_textdomain() {
    load_plugin_textdomain('schema-validator-pro', false, dirname(plugin_basename(__FILE__)) . '/languages');
}
add_action('plugins_loaded', 'svp_load_textdomain');

/**
 * Auto-inject Schema JSON-LD into page head
 * This is the core functionality - automatically adds schema markup
 */
function svp_inject_schema() {
    if (!is_singular()) {
        return; // Only inject on single posts/pages
    }

    global $post;
    if (!$post) {
        return;
    }

    // Get stored schema from post meta
    $schema = get_post_meta($post->ID, '_svp_schema', true);

    if (empty($schema)) {
        return;
    }

    // Decode if it's JSON string
    if (is_string($schema)) {
        $schema_data = json_decode($schema, true);
    } else {
        $schema_data = $schema;
    }

    if (empty($schema_data)) {
        return;
    }

    // Check if schema already exists in the page (prevent duplicate injection)
    if (svp_has_existing_schema()) {
        return;
    }

    // Allow filtering schema data before injection
    $schema_data = apply_filters('svp_schema_data', $schema_data, $post->ID);

    // Fire action before injection
    do_action('svp_before_schema_injection', $schema_data, $post->ID);

    // Output schema as JSON-LD (using wp_json_encode for security)
    echo "\n<!-- Schema Validator Pro v" . esc_attr(SCHEMA_VALIDATOR_PRO_VERSION) . " -->\n";
    echo '<script type="application/ld+json">';
    echo wp_json_encode($schema_data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    echo '</script>';
    echo "\n<!-- /Schema Validator Pro -->\n";

    // Fire action after injection
    do_action('svp_after_schema_injection', $schema_data, $post->ID);
}
add_action('wp_head', 'svp_inject_schema');

/**
 * Check if page already has schema markup (prevent duplicates)
 *
 * @return bool True if schema exists, false otherwise
 */
function svp_has_existing_schema() {
    global $post;

    // Check if other plugins have already injected schema
    // This is a simple check - can be enhanced with more sophisticated detection
    $has_schema = false;

    // Allow other plugins to indicate they've added schema
    $has_schema = apply_filters('svp_has_existing_schema', $has_schema, $post->ID);

    return $has_schema;
}

/**
 * Enqueue admin scripts and styles
 */
function svp_enqueue_admin_assets($hook) {
    // Only load on post edit screens
    if (!in_array($hook, ['post.php', 'post-new.php'])) {
        return;
    }

    // Enqueue metabox CSS
    wp_enqueue_style(
        'svp-metabox',
        SCHEMA_VALIDATOR_PRO_URL . 'assets/admin/css/metabox.css',
        [],
        SCHEMA_VALIDATOR_PRO_VERSION
    );

    // Enqueue metabox JS
    wp_enqueue_script(
        'svp-metabox',
        SCHEMA_VALIDATOR_PRO_URL . 'assets/admin/js/metabox.js',
        ['jquery'],
        SCHEMA_VALIDATOR_PRO_VERSION,
        true
    );

    // Localize script with data and i18n strings
    global $post;
    wp_localize_script('svp-metabox', 'svpMetaboxData', [
        'postId' => $post ? $post->ID : 0,
        'nonce' => wp_create_nonce('svp_generate_schema'),
        'i18n' => [
            'generateButton' => __('Generate Schema', 'schema-validator-pro'),
            'generating' => __('Generating...', 'schema-validator-pro'),
            'generatingMessage' => __('Generating schema...', 'schema-validator-pro'),
            'retrying' => __('Retrying...', 'schema-validator-pro'),
            'retryingMessage' => __('Request failed, retrying in', 'schema-validator-pro'),
            'retryAfter' => __('Please retry after %s seconds.', 'schema-validator-pro'),
            'networkError' => __('Network error. Please try again.', 'schema-validator-pro'),
            'unknownError' => __('Unknown error occurred.', 'schema-validator-pro'),
        ]
    ]);
}
add_action('admin_enqueue_scripts', 'svp_enqueue_admin_assets');

/**
 * Enqueue admin page styles
 */
function svp_enqueue_admin_page_assets($hook) {
    // Only load on our admin pages
    if (strpos($hook, 'schema-validator-pro') === false) {
        return;
    }

    wp_enqueue_style(
        'svp-admin',
        SCHEMA_VALIDATOR_PRO_URL . 'assets/admin/css/admin.css',
        [],
        SCHEMA_VALIDATOR_PRO_VERSION
    );
}
add_action('admin_enqueue_scripts', 'svp_enqueue_admin_page_assets');

/**
 * Add Schema meta box to post editor
 */
function svp_add_meta_box() {
    add_meta_box(
        'svp_schema_metabox',
        __('Schema Validator Pro', 'schema-validator-pro'),
        'svp_schema_metabox_callback',
        ['post', 'page'],
        'side',
        'default'
    );
}
add_action('add_meta_boxes', 'svp_add_meta_box');

/**
 * Render the Schema meta box
 */
function svp_schema_metabox_callback($post) {
    wp_nonce_field('svp_schema_metabox', 'svp_schema_metabox_nonce');

    $schema = get_post_meta($post->ID, '_svp_schema', true);
    $schema_type = get_post_meta($post->ID, '_svp_schema_type', true);
    $generated_at = get_post_meta($post->ID, '_svp_schema_generated_at', true);

    // Get available schema types (filterable)
    $schema_types = apply_filters('svp_schema_types', [
        'Article' => __('Article', 'schema-validator-pro'),
        'Product' => __('Product', 'schema-validator-pro'),
        'Recipe' => __('Recipe', 'schema-validator-pro'),
        'HowTo' => __('HowTo', 'schema-validator-pro'),
        'FAQPage' => __('FAQ Page', 'schema-validator-pro'),
        'Event' => __('Event', 'schema-validator-pro'),
        'Person' => __('Person', 'schema-validator-pro'),
        'Organization' => __('Organization', 'schema-validator-pro'),
        'Course' => __('Course', 'schema-validator-pro'),
    ]);

    ?>
    <div class="svp-schema-metabox">
        <p>
            <label for="svp_schema_type"><?php esc_html_e('Schema Type:', 'schema-validator-pro'); ?></label>
            <select id="svp_schema_type" name="svp_schema_type">
                <option value=""><?php esc_html_e('Auto-detect', 'schema-validator-pro'); ?></option>
                <?php foreach ($schema_types as $type => $label): ?>
                    <option value="<?php echo esc_attr($type); ?>" <?php selected($schema_type, $type); ?>>
                        <?php echo esc_html($label); ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </p>

        <p>
            <button type="button" id="svp-generate-schema-btn" class="button button-primary">
                <?php esc_html_e('Generate Schema', 'schema-validator-pro'); ?>
            </button>
        </p>

        <div id="svp-schema-status"></div>

        <?php if ($schema): ?>
            <div class="svp-schema-info">
                <strong><?php esc_html_e('Status:', 'schema-validator-pro'); ?></strong>
                <span class="dashicons dashicons-yes"></span>
                <?php esc_html_e('Schema generated', 'schema-validator-pro'); ?><br>

                <strong><?php esc_html_e('Type:', 'schema-validator-pro'); ?></strong>
                <?php echo esc_html($schema_type); ?><br>

                <?php if ($generated_at): ?>
                    <strong><?php esc_html_e('Generated:', 'schema-validator-pro'); ?></strong>
                    <?php echo esc_html(mysql2date(get_option('date_format') . ' ' . get_option('time_format'), $generated_at)); ?><br>
                <?php endif; ?>

                <details class="svp-schema-preview">
                    <summary><?php esc_html_e('View Schema JSON', 'schema-validator-pro'); ?></summary>
                    <pre><?php echo esc_html($schema); ?></pre>
                </details>
            </div>
        <?php endif; ?>
    </div>
    <?php
}

/**
 * Add admin menu
 */
function svp_add_admin_menu() {
    add_menu_page(
        __('Schema Validator Pro', 'schema-validator-pro'),
        __('Schema Pro', 'schema-validator-pro'),
        'manage_options',
        'schema-validator-pro',
        'svp_admin_page',
        'dashicons-code-standards'
    );

    add_submenu_page(
        'schema-validator-pro',
        __('Settings', 'schema-validator-pro'),
        __('Settings', 'schema-validator-pro'),
        'manage_options',
        'schema-validator-pro-settings',
        'svp_settings_page'
    );
}
add_action('admin_menu', 'svp_add_admin_menu');

/**
 * Register settings
 */
function svp_register_settings() {
    register_setting('svp_settings', 'svp_api_endpoint', [
        'type' => 'string',
        'default' => 'http://localhost:8000',
        'sanitize_callback' => 'esc_url_raw'
    ]);

    register_setting('svp_settings', 'svp_api_key', [
        'type' => 'string',
        'default' => '',
        'sanitize_callback' => 'sanitize_text_field'
    ]);
}
add_action('admin_init', 'svp_register_settings');

/**
 * Settings page
 */
function svp_settings_page() {
    if (!current_user_can('manage_options')) {
        wp_die(__('You do not have sufficient permissions to access this page.', 'schema-validator-pro'));
    }

    // Handle clear cache action
    if (isset($_POST['svp_clear_cache'])) {
        check_admin_referer('svp_clear_cache_action', 'svp_clear_cache_nonce');

        global $wpdb;
        $deleted = $wpdb->query(
            $wpdb->prepare(
                "DELETE FROM {$wpdb->options} WHERE option_name LIKE %s OR option_name LIKE %s",
                svp_esc_like('_transient_svp_schema_') . '%',
                svp_esc_like('_transient_timeout_svp_schema_') . '%'
            )
        );

        echo '<div class="notice notice-success is-dismissible"><p>' .
             sprintf(
                 /* translators: %d: number of cache entries cleared */
                 esc_html__('Cache cleared successfully! (%d entries removed)', 'schema-validator-pro'),
                 $deleted
             ) .
             '</p></div>';
    }

    // Save settings
    if (isset($_POST['svp_settings_submit'])) {
        check_admin_referer('svp_settings_action', 'svp_settings_nonce');

        $endpoint = isset($_POST['svp_api_endpoint']) ? esc_url_raw($_POST['svp_api_endpoint']) : '';
        update_option('svp_api_endpoint', $endpoint);

        $api_key = isset($_POST['svp_api_key']) ? sanitize_text_field($_POST['svp_api_key']) : '';
        update_option('svp_api_key', $api_key);

        echo '<div class="notice notice-success is-dismissible"><p>' .
             esc_html__('Settings saved successfully!', 'schema-validator-pro') .
             '</p></div>';
    }

    $endpoint = get_option('svp_api_endpoint', 'http://localhost:8000');
    $api_key = get_option('svp_api_key', '');

    ?>
    <div class="wrap svp-settings-page">
        <h1><?php echo esc_html(get_admin_page_title()); ?></h1>

        <form method="post" action="">
            <?php wp_nonce_field('svp_settings_action', 'svp_settings_nonce'); ?>

            <table class="form-table" role="presentation">
                <tr>
                    <th scope="row">
                        <label for="svp_api_endpoint">
                            <?php esc_html_e('API Endpoint', 'schema-validator-pro'); ?>
                        </label>
                    </th>
                    <td>
                        <input type="url"
                               id="svp_api_endpoint"
                               name="svp_api_endpoint"
                               value="<?php echo esc_attr($endpoint); ?>"
                               class="regular-text"
                               required
                               placeholder="http://localhost:8000" />
                        <p class="description">
                            <?php esc_html_e('Backend API endpoint URL (e.g., http://localhost:8000 or https://api.yoursite.com)', 'schema-validator-pro'); ?>
                        </p>
                    </td>
                </tr>
                <tr>
                    <th scope="row">
                        <label for="svp_api_key">
                            <?php esc_html_e('API Key', 'schema-validator-pro'); ?>
                        </label>
                    </th>
                    <td>
                        <input type="password"
                               id="svp_api_key"
                               name="svp_api_key"
                               value="<?php echo esc_attr($api_key); ?>"
                               class="regular-text"
                               placeholder="<?php esc_attr_e('Optional - leave empty if not required', 'schema-validator-pro'); ?>" />
                        <p class="description">
                            <?php esc_html_e('API authentication key (optional, only required if backend has API_KEY configured)', 'schema-validator-pro'); ?>
                        </p>
                    </td>
                </tr>
            </table>

            <?php submit_button(__('Save Settings', 'schema-validator-pro'), 'primary', 'svp_settings_submit'); ?>
        </form>

        <hr>

        <h2><?php esc_html_e('Cache Management', 'schema-validator-pro'); ?></h2>
        <p><?php esc_html_e('Clear all cached schemas. Schemas are automatically cached for 1 hour to improve performance and provide fallback when API is unavailable.', 'schema-validator-pro'); ?></p>
        <form method="post" action="" style="margin-top: 10px;">
            <?php wp_nonce_field('svp_clear_cache_action', 'svp_clear_cache_nonce'); ?>
            <?php submit_button(__('Clear All Cache', 'schema-validator-pro'), 'secondary', 'svp_clear_cache', false); ?>
        </form>

        <hr>

        <h2><?php esc_html_e('API Status', 'schema-validator-pro'); ?></h2>
        <p>
            <?php
            $status = svp_check_api_status($endpoint);
            if ($status['available']) {
                echo '<span style="color: #46b450;">✓ ' . esc_html__('API is available', 'schema-validator-pro') . '</span>';
            } else {
                echo '<span style="color: #dc3232;">✗ ' . esc_html__('API is not available', 'schema-validator-pro') . '</span>';
                if (!empty($status['error'])) {
                    echo '<br><small>' . esc_html($status['error']) . '</small>';
                }
            }
            ?>
        </p>
    </div>
    <?php
}

/**
 * Check API status
 *
 * @param string $endpoint API endpoint URL
 * @return array Status information
 */
function svp_check_api_status($endpoint) {
    if (empty($endpoint)) {
        return ['available' => false, 'error' => __('No endpoint configured', 'schema-validator-pro')];
    }

    $response = wp_remote_get($endpoint . '/health', [
        'timeout' => 5,
        'sslverify' => apply_filters('svp_api_sslverify', true)
    ]);

    if (is_wp_error($response)) {
        return ['available' => false, 'error' => $response->get_error_message()];
    }

    $code = wp_remote_retrieve_response_code($response);
    if ($code === 200) {
        return ['available' => true];
    }

    return ['available' => false, 'error' => sprintf(__('HTTP %d', 'schema-validator-pro'), $code)];
}

/**
 * Main admin page
 */
function svp_admin_page() {
    ?>
    <div class="wrap svp-admin-page">
        <h1><?php echo esc_html(get_admin_page_title()); ?></h1>
        <p><?php esc_html_e('WordPress Schema.org Auto-Injection Tool', 'schema-validator-pro'); ?></p>

        <div class="card">
            <h2><?php esc_html_e('How It Works', 'schema-validator-pro'); ?></h2>
            <ol>
                <li><?php esc_html_e('Edit any post or page', 'schema-validator-pro'); ?></li>
                <li><?php esc_html_e('Click "Generate Schema" in the Schema Validator Pro meta box', 'schema-validator-pro'); ?></li>
                <li><?php esc_html_e('Schema is automatically injected into your page\'s <head> section', 'schema-validator-pro'); ?></li>
                <li><?php esc_html_e('Google and other search engines can now understand your content better!', 'schema-validator-pro'); ?></li>
            </ol>
        </div>

        <div class="card">
            <h2><?php esc_html_e('Supported Schema Types', 'schema-validator-pro'); ?></h2>
            <ul>
                <li><strong><?php esc_html_e('Article', 'schema-validator-pro'); ?></strong> - <?php esc_html_e('Blog posts, news articles', 'schema-validator-pro'); ?></li>
                <li><strong><?php esc_html_e('Product', 'schema-validator-pro'); ?></strong> - <?php esc_html_e('E-commerce products', 'schema-validator-pro'); ?></li>
                <li><strong><?php esc_html_e('Recipe', 'schema-validator-pro'); ?></strong> - <?php esc_html_e('Cooking recipes', 'schema-validator-pro'); ?></li>
                <li><strong><?php esc_html_e('HowTo', 'schema-validator-pro'); ?></strong> - <?php esc_html_e('Step-by-step guides', 'schema-validator-pro'); ?></li>
                <li><strong><?php esc_html_e('FAQPage', 'schema-validator-pro'); ?></strong> - <?php esc_html_e('Frequently asked questions', 'schema-validator-pro'); ?></li>
                <li><strong><?php esc_html_e('Event', 'schema-validator-pro'); ?></strong> - <?php esc_html_e('Events and conferences', 'schema-validator-pro'); ?></li>
                <li><strong><?php esc_html_e('Person', 'schema-validator-pro'); ?></strong> - <?php esc_html_e('Author profiles', 'schema-validator-pro'); ?></li>
                <li><strong><?php esc_html_e('Organization', 'schema-validator-pro'); ?></strong> - <?php esc_html_e('Company information', 'schema-validator-pro'); ?></li>
                <li><strong><?php esc_html_e('Course', 'schema-validator-pro'); ?></strong> - <?php esc_html_e('Educational courses', 'schema-validator-pro'); ?></li>
            </ul>
        </div>

        <div class="card">
            <h2><?php esc_html_e('Need Help?', 'schema-validator-pro'); ?></h2>
            <p>
                <?php
                printf(
                    /* translators: %s: Schema.org URL */
                    esc_html__('Visit %s to learn more about structured data.', 'schema-validator-pro'),
                    '<a href="https://schema.org" target="_blank" rel="noopener noreferrer">Schema.org</a>'
                );
                ?>
            </p>
            <p>
                <?php
                printf(
                    /* translators: %s: Google Rich Results Test URL */
                    esc_html__('Use %s to validate your schema.', 'schema-validator-pro'),
                    '<a href="https://search.google.com/test/rich-results" target="_blank" rel="noopener noreferrer">' . esc_html__('Google\'s Rich Results Test', 'schema-validator-pro') . '</a>'
                );
                ?>
            </p>
        </div>
    </div>
    <?php
}

/**
 * Get cache key for schema
 */
function svp_get_schema_cache_key($post_id, $schema_type) {
    return 'svp_schema_' . $post_id . '_' . $schema_type;
}

/**
 * Get cached schema
 */
function svp_get_cached_schema($post_id, $schema_type) {
    $cache_key = svp_get_schema_cache_key($post_id, $schema_type);
    return get_transient($cache_key);
}

/**
 * Set cached schema
 */
function svp_set_cached_schema($post_id, $schema_type, $schema_data, $expiration = 3600) {
    $cache_key = svp_get_schema_cache_key($post_id, $schema_type);
    return set_transient($cache_key, $schema_data, $expiration);
}

/**
 * Clear cached schema
 */
function svp_clear_cached_schema($post_id, $schema_type = null) {
    if ($schema_type) {
        // Clear specific schema type
        $cache_key = svp_get_schema_cache_key($post_id, $schema_type);
        delete_transient($cache_key);
    } else {
        // Clear all schema types for this post using single query
        global $wpdb;

        $pattern = svp_esc_like('_transient_svp_schema_' . $post_id . '_') . '%';
        $timeout_pattern = svp_esc_like('_transient_timeout_svp_schema_' . $post_id . '_') . '%';

        $deleted = $wpdb->query(
            $wpdb->prepare(
                "DELETE FROM {$wpdb->options} WHERE option_name LIKE %s OR option_name LIKE %s",
                $pattern,
                $timeout_pattern
            )
        );

        // Clear object cache if available
        if (function_exists('wp_cache_flush_group')) {
            wp_cache_flush_group('svp_schema');
        }

        return $deleted;
    }
}

/**
 * Clear schema cache when post is updated
 */
function svp_clear_cache_on_post_update($post_id) {
    svp_clear_cached_schema($post_id);
}
add_action('save_post', 'svp_clear_cache_on_post_update');

/**
 * AJAX handler for schema generation
 */
function svp_ajax_generate_schema() {
    $logger = svp_logger();
    $start_time = microtime(true);

    // Verify nonce
    check_ajax_referer('svp_generate_schema');

    // Get and validate post ID
    $post_id = isset($_POST['post_id']) ? intval($_POST['post_id']) : 0;

    if (!$post_id) {
        $logger->error('Invalid post ID in schema generation request', array(
            'post_id' => $post_id,
        ));
        wp_send_json_error(__('Invalid post ID', 'schema-validator-pro'));
        return;
    }

    // Check permissions
    if (!current_user_can('edit_post', $post_id)) {
        $logger->warning('Permission denied for schema generation', array(
            'post_id' => $post_id,
            'user_id' => get_current_user_id(),
        ));
        wp_send_json_error(__('Permission denied', 'schema-validator-pro'));
        return;
    }

    // Get post
    $post = get_post($post_id);
    if (!$post) {
        wp_send_json_error(__('Post not found', 'schema-validator-pro'));
        return;
    }

    // Get and validate schema type
    $schema_type = isset($_POST['schema_type']) ? sanitize_text_field($_POST['schema_type']) : 'Article';

    // Check if force regenerate (bypass cache)
    $force_regenerate = isset($_POST['force']) && $_POST['force'] === 'true';

    // Try to get cached schema first (unless force regenerate)
    if (!$force_regenerate) {
        $cached_schema = svp_get_cached_schema($post_id, $schema_type);
        if ($cached_schema !== false) {
            $duration_ms = round((microtime(true) - $start_time) * 1000, 2);
            $logger->info('Schema retrieved from cache', array(
                'post_id' => $post_id,
                'schema_type' => $schema_type,
                'duration_ms' => $duration_ms,
                'cache_hit' => true,
            ));

            wp_send_json_success([
                'message' => __('Schema retrieved from cache', 'schema-validator-pro'),
                'schema' => $cached_schema,
                'cached' => true
            ]);
            return;
        } else {
            $logger->debug('Cache miss for schema', array(
                'post_id' => $post_id,
                'schema_type' => $schema_type,
            ));
        }
    }

    // Get API endpoint
    $endpoint = apply_filters('svp_api_endpoint', get_option('svp_api_endpoint', ''));
    if (empty($endpoint)) {
        // Try to use cached schema as fallback
        $cached_schema = svp_get_cached_schema($post_id, $schema_type);
        if ($cached_schema !== false) {
            wp_send_json_success([
                'message' => __('API not available. Using cached schema.', 'schema-validator-pro'),
                'schema' => $cached_schema,
                'cached' => true,
                'fallback' => true
            ]);
            return;
        }

        wp_send_json_error(__('API not configured. Please configure in Settings.', 'schema-validator-pro'));
        return;
    }

    // Prepare content
    $title = $post->post_title;
    $body = wp_strip_all_tags($post->post_content);
    $content = $title . "\n\n" . $body;

    // Prepare metadata
    $metadata = [
        'author' => get_the_author_meta('display_name', $post->post_author),
        'datePublished' => get_the_date('c', $post_id), // ISO 8601 format
    ];

    // Allow filtering metadata
    $metadata = apply_filters('svp_schema_metadata', $metadata, $post_id);

    // Prepare API request body
    $request_body = [
        'schema_type' => $schema_type,
        'content' => $content,
        'url' => get_permalink($post_id),
        'metadata' => $metadata
    ];

    // Allow filtering request body
    $request_body = apply_filters('svp_api_request_body', $request_body, $post_id);

    // Prepare headers
    $headers = ['Content-Type' => 'application/json'];

    // Add API key if configured
    $api_key = get_option('svp_api_key', '');
    if (!empty($api_key)) {
        $headers['X-API-Key'] = $api_key;
    }

    // Call API
    $response = wp_remote_post($endpoint . '/api/v1/schema/generate', [
        'headers' => $headers,
        'body' => wp_json_encode($request_body),
        'timeout' => 30,
        'sslverify' => apply_filters('svp_api_sslverify', true)
    ]);

    // Handle network errors - try cache fallback
    if (is_wp_error($response)) {
        // Try to use cached schema as fallback
        $cached_schema = svp_get_cached_schema($post_id, $schema_type);
        if ($cached_schema !== false) {
            wp_send_json_success([
                'message' => __('Network error. Using cached schema.', 'schema-validator-pro'),
                'schema' => $cached_schema,
                'cached' => true,
                'fallback' => true
            ]);
            return;
        }

        wp_send_json_error(
            sprintf(
                /* translators: %s: error message */
                __('Network error: %s', 'schema-validator-pro'),
                $response->get_error_message()
            )
        );
        return;
    }

    // Check HTTP status code - try cache fallback for 5xx errors
    $code = wp_remote_retrieve_response_code($response);
    if ($code !== 200) {
        // For 5xx errors, try cache fallback
        if ($code >= 500 && $code < 600) {
            $cached_schema = svp_get_cached_schema($post_id, $schema_type);
            if ($cached_schema !== false) {
                wp_send_json_success([
                    'message' => __('API temporarily unavailable. Using cached schema.', 'schema-validator-pro'),
                    'schema' => $cached_schema,
                    'cached' => true,
                    'fallback' => true
                ]);
                return;
            }
        }

        $body = wp_remote_retrieve_body($response);
        $error_data = json_decode($body, true);
        $error_message = isset($error_data['detail']) ? $error_data['detail'] : sprintf(__('API error (HTTP %d)', 'schema-validator-pro'), $code);

        wp_send_json_error($error_message);
        return;
    }

    // Parse response
    $data = json_decode(wp_remote_retrieve_body($response), true);
    if (!$data || !isset($data['schema'])) {
        wp_send_json_error(__('Invalid API response', 'schema-validator-pro'));
        return;
    }

    // Save schema (using wp_json_encode for security)
    update_post_meta($post_id, '_svp_schema', wp_json_encode($data['schema'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
    update_post_meta($post_id, '_svp_schema_type', $schema_type);
    update_post_meta($post_id, '_svp_schema_generated_at', current_time('mysql'));
    update_post_meta($post_id, '_svp_schema_version', SCHEMA_VALIDATOR_PRO_VERSION);

    // Cache the schema (1 hour expiration)
    svp_set_cached_schema($post_id, $schema_type, $data['schema'], 3600);

    // Fire action after schema generation
    do_action('svp_schema_generated', $data['schema'], $post_id);

    // Send success response
    wp_send_json_success([
        'schema' => $data['schema'],
        'message' => __('Schema generated successfully!', 'schema-validator-pro'),
        'cached' => false
    ]);
}
add_action('wp_ajax_svp_generate_schema', 'svp_ajax_generate_schema');

