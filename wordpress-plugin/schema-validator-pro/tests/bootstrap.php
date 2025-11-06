<?php
/**
 * PHPUnit Bootstrap File
 * Sets up the testing environment for Schema Validator Pro
 */

// Require Composer autoloader
require_once dirname(__DIR__) . '/vendor/autoload.php';

// Initialize Brain Monkey for WordPress function mocking
\Brain\Monkey\setUp();

// Define WordPress constants that the plugin expects
if (!defined('ABSPATH')) {
    define('ABSPATH', '/tmp/wordpress/');
}

if (!defined('WPINC')) {
    define('WPINC', 'wp-includes');
}

if (!defined('OBJECT')) {
    define('OBJECT', 'OBJECT');
}

if (!defined('ARRAY_A')) {
    define('ARRAY_A', 'ARRAY_A');
}

if (!defined('ARRAY_N')) {
    define('ARRAY_N', 'ARRAY_N');
}

// Define plugin constants
define('SCHEMA_VALIDATOR_PRO_VERSION', '1.0.0');
define('SCHEMA_VALIDATOR_PRO_FILE', dirname(__DIR__) . '/schema-validator-pro.php');
define('SCHEMA_VALIDATOR_PRO_DIR', dirname(__DIR__) . '/');
define('SCHEMA_VALIDATOR_PRO_URL', 'http://example.com/wp-content/plugins/schema-validator-pro/');

// Global test variables
global $test_post_meta, $test_is_singular, $test_transients, $test_options, $test_ajax_response, $test_wp_remote_response, $test_user_can, $test_wp_die_called, $test_wpdb_query_result, $test_load_textdomain_called, $test_add_menu_page_called, $test_register_setting_called, $test_add_meta_box_called, $test_wp_enqueue_style_called;
$test_post_meta = [];
$test_is_singular = false;
$test_transients = [];
$test_options = [];
$test_ajax_response = null;
$test_wp_remote_response = null;
$test_user_can = true;
$test_wp_die_called = false;
$test_wpdb_query_result = 0;
$test_load_textdomain_called = false;
$test_add_menu_page_called = false;
$test_register_setting_called = false;
$test_add_meta_box_called = false;
$test_wp_enqueue_style_called = false;

/**
 * Mock WordPress functions that are commonly used
 */

// Mock plugin_dir_path
if (!function_exists('plugin_dir_path')) {
    function plugin_dir_path($file) {
        return dirname($file) . '/';
    }
}

// Mock plugin_dir_url
if (!function_exists('plugin_dir_url')) {
    function plugin_dir_url($file) {
        return 'http://example.com/wp-content/plugins/' . basename(dirname($file)) . '/';
    }
}

// Mock plugin_basename
if (!function_exists('plugin_basename')) {
    function plugin_basename($file) {
        return 'schema-validator-pro/schema-validator-pro.php';
    }
}

// Mock esc_attr
if (!function_exists('esc_attr')) {
    function esc_attr($text) {
        return htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
    }
}

// Mock esc_html
if (!function_exists('esc_html')) {
    function esc_html($text) {
        return htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
    }
}

// Mock esc_url_raw - removed duplicate, see line 823 for actual implementation

// Mock sanitize_text_field
if (!function_exists('sanitize_text_field')) {
    function sanitize_text_field($str) {
        return strip_tags($str);
    }
}

// Mock wp_json_encode
if (!function_exists('wp_json_encode')) {
    function wp_json_encode($data, $options = 0, $depth = 512) {
        return json_encode($data, $options, $depth);
    }
}

// Mock wp_strip_all_tags
if (!function_exists('wp_strip_all_tags')) {
    function wp_strip_all_tags($string, $remove_breaks = false) {
        $string = preg_replace('@<(script|style)[^>]*?>.*?</\\1>@si', '', $string);
        $string = strip_tags($string);
        if ($remove_breaks) {
            $string = preg_replace('/[\r\n\t ]+/', ' ', $string);
        }
        return trim($string);
    }
}

// Mock current_time
if (!function_exists('current_time')) {
    function current_time($type, $gmt = 0) {
        if ($type === 'mysql') {
            return date('Y-m-d H:i:s');
        }
        return time();
    }
}

// Mock mysql2date
if (!function_exists('mysql2date')) {
    function mysql2date($format, $date) {
        $timestamp = strtotime($date);
        return date($format, $timestamp);
    }
}

// Mock get_option - removed duplicate, see line 369 for actual implementation

// Mock update_option (will be overridden in tests)
if (!function_exists('update_option')) {
    function update_option($option, $value, $autoload = null) {
        global $test_options;
        $test_options[$option] = $value;
        return true;
    }
}

// Mock get_post_meta (will be overridden in tests)
if (!function_exists('get_post_meta')) {
    function get_post_meta($post_id, $key = '', $single = false) {
        global $test_post_meta;

        if (isset($test_post_meta[$post_id][$key])) {
            $value = $test_post_meta[$post_id][$key];
            return $single ? $value[0] : $value;
        }

        return $single ? '' : [];
    }
}

// Mock update_post_meta (will be overridden in tests)
if (!function_exists('update_post_meta')) {
    function update_post_meta($post_id, $meta_key, $meta_value, $prev_value = '') {
        return true;
    }
}

// Mock get_transient (will be overridden in tests)
if (!function_exists('get_transient')) {
    function get_transient($transient) {
        global $test_transients;
        return isset($test_transients[$transient]) ? $test_transients[$transient] : false;
    }
}

// Mock set_transient (will be overridden in tests)
if (!function_exists('set_transient')) {
    function set_transient($transient, $value, $expiration = 0) {
        global $test_transients;
        $test_transients[$transient] = $value;
        return true;
    }
}

// Mock delete_transient (will be overridden in tests)
if (!function_exists('delete_transient')) {
    function delete_transient($transient) {
        global $test_transients;
        unset($test_transients[$transient]);
        return true;
    }
}

// Mock is_singular - removed duplicate, see line 274 for actual implementation

// Mock wp_upload_dir (will be overridden in tests)
if (!function_exists('wp_upload_dir')) {
    function wp_upload_dir($time = null, $create_dir = true, $refresh_cache = false) {
        return [
            'path' => '/tmp/wordpress/wp-content/uploads',
            'url' => 'http://example.com/wp-content/uploads',
            'subdir' => '',
            'basedir' => '/tmp/wordpress/wp-content/uploads',
            'baseurl' => 'http://example.com/wp-content/uploads',
            'error' => false,
        ];
    }
}

// Mock wp_mkdir_p
if (!function_exists('wp_mkdir_p')) {
    function wp_mkdir_p($target) {
        if (file_exists($target)) {
            return @is_dir($target);
        }
        $target = str_replace('//', '/', $target);
        $target = rtrim($target, '/');
        if (empty($target)) {
            $target = '/';
        }
        if (file_exists($target)) {
            return @is_dir($target);
        }
        $dir = dirname($target);
        if ($dir === $target) {
            return false;
        }
        if (wp_mkdir_p($dir)) {
            return @mkdir($target, 0755);
        }
        return false;
    }
}

// Mock __() for i18n
if (!function_exists('__')) {
    function __($text, $domain = 'default') {
        return $text;
    }
}

// Mock _e() for i18n
if (!function_exists('_e')) {
    function _e($text, $domain = 'default') {
        echo $text;
    }
}

// Mock esc_html__
if (!function_exists('esc_html__')) {
    function esc_html__($text, $domain = 'default') {
        return esc_html($text);
    }
}

// Mock esc_html_e
if (!function_exists('esc_html_e')) {
    function esc_html_e($text, $domain = 'default') {
        echo esc_html($text);
    }
}

// Mock esc_attr__
if (!function_exists('esc_attr__')) {
    function esc_attr__($text, $domain = 'default') {
        return esc_attr($text);
    }
}

// Mock esc_attr_e
if (!function_exists('esc_attr_e')) {
    function esc_attr_e($text, $domain = 'default') {
        echo esc_attr($text);
    }
}

// Mock get_current_user_id
if (!function_exists('get_current_user_id')) {
    function get_current_user_id() {
        return 1; // Default test user ID
    }
}

// Mock is_singular
if (!function_exists('is_singular')) {
    function is_singular($post_types = '') {
        global $test_is_singular;
        return isset($test_is_singular) ? $test_is_singular : true;
    }
}

// Mock apply_filters
if (!function_exists('apply_filters')) {
    function apply_filters($tag, $value, ...$args) {
        return $value;
    }
}

// Mock do_action
if (!function_exists('do_action')) {
    function do_action($tag, ...$args) {
        // No-op for testing
    }
}

// Mock get_post - removed duplicate, see line 341 for actual implementation

// Mock current_user_can - removed duplicate, see line 333 for actual implementation

// Mock check_ajax_referer
if (!function_exists('check_ajax_referer')) {
    function check_ajax_referer($action = -1, $query_arg = false, $die = true) {
        return true;
    }
}

// Mock check_admin_referer
if (!function_exists('check_admin_referer')) {
    function check_admin_referer($action = -1, $query_arg = '_wpnonce') {
        return true;
    }
}

// Mock wp_send_json_success
if (!function_exists('wp_send_json_success')) {
    function wp_send_json_success($data = null, $status_code = null) {
        global $test_ajax_response;
        $test_ajax_response = [
            'success' => true,
            'data' => $data,
        ];
    }
}

// Mock wp_send_json_error
if (!function_exists('wp_send_json_error')) {
    function wp_send_json_error($data = null, $status_code = null) {
        global $test_ajax_response;
        $test_ajax_response = [
            'success' => false,
            'data' => $data,
        ];
    }
}

// Mock current_user_can
if (!function_exists('current_user_can')) {
    function current_user_can($capability, ...$args) {
        global $test_user_can;
        return isset($test_user_can) ? $test_user_can : true;
    }
}

// Mock get_post
if (!function_exists('get_post')) {
    function get_post($post = null, $output = OBJECT, $filter = 'raw') {
        global $test_get_post;
        if (isset($test_get_post)) {
            return $test_get_post;
        }
        return (object) [
            'ID' => $post,
            'post_title' => 'Test Post',
            'post_content' => 'Test content',
            'post_author' => 1,
        ];
    }
}

// Mock sanitize_text_field
if (!function_exists('sanitize_text_field')) {
    function sanitize_text_field($str) {
        return strip_tags($str);
    }
}

// Mock get_option
if (!function_exists('get_option')) {
    function get_option($option, $default = false) {
        global $test_options;
        return isset($test_options[$option]) ? $test_options[$option] : $default;
    }
}

// Mock wp_remote_post
if (!function_exists('wp_remote_post')) {
    function wp_remote_post($url, $args = []) {
        global $test_wp_remote_response;
        if (isset($test_wp_remote_response)) {
            return $test_wp_remote_response;
        }
        return new WP_Error('http_request_failed', 'Test error');
    }
}

// Mock wp_remote_retrieve_response_code
if (!function_exists('wp_remote_retrieve_response_code')) {
    function wp_remote_retrieve_response_code($response) {
        if (is_wp_error($response)) {
            return 0;
        }
        return isset($response['response']['code']) ? $response['response']['code'] : 200;
    }
}

// Mock wp_remote_retrieve_body
if (!function_exists('wp_remote_retrieve_body')) {
    function wp_remote_retrieve_body($response) {
        if (is_wp_error($response)) {
            return '';
        }
        return isset($response['body']) ? $response['body'] : '';
    }
}

// Mock get_the_author_meta
if (!function_exists('get_the_author_meta')) {
    function get_the_author_meta($field = '', $user_id = false) {
        return 'Test Author';
    }
}

// Mock get_the_date
if (!function_exists('get_the_date')) {
    function get_the_date($format = '', $post = null) {
        return date($format ?: 'Y-m-d');
    }
}

// Mock get_permalink
if (!function_exists('get_permalink')) {
    function get_permalink($post = 0, $leavename = false) {
        return 'http://example.com/test-post/';
    }
}

// Mock current_time
if (!function_exists('current_time')) {
    function current_time($type, $gmt = 0) {
        if ($type === 'mysql') {
            return date('Y-m-d H:i:s');
        }
        return time();
    }
}

// Mock wp_enqueue_style
if (!function_exists('wp_enqueue_style')) {
    function wp_enqueue_style($handle, $src = '', $deps = [], $ver = false, $media = 'all') {
        global $test_enqueued_styles, $test_wp_enqueue_style_called;
        $test_wp_enqueue_style_called = true;
        $test_enqueued_styles[$handle] = [
            'src' => $src,
            'deps' => $deps,
            'ver' => $ver,
            'media' => $media,
        ];
    }
}

// Mock wp_enqueue_script
if (!function_exists('wp_enqueue_script')) {
    function wp_enqueue_script($handle, $src = '', $deps = [], $ver = false, $in_footer = false) {
        global $test_enqueued_scripts;
        $test_enqueued_scripts[$handle] = [
            'src' => $src,
            'deps' => $deps,
            'ver' => $ver,
            'in_footer' => $in_footer,
        ];
    }
}

// Mock wp_localize_script
if (!function_exists('wp_localize_script')) {
    function wp_localize_script($handle, $object_name, $l10n) {
        global $test_localized_scripts;
        $test_localized_scripts[$handle] = [
            'object_name' => $object_name,
            'data' => $l10n,
        ];
    }
}

// Mock wp_create_nonce
if (!function_exists('wp_create_nonce')) {
    function wp_create_nonce($action = -1) {
        return 'test_nonce_' . md5($action);
    }
}

// Mock wp_nonce_field
if (!function_exists('wp_nonce_field')) {
    function wp_nonce_field($action = -1, $name = '_wpnonce', $referer = true, $echo = true) {
        $nonce = wp_create_nonce($action);
        $output = '<input type="hidden" name="' . esc_attr($name) . '" value="' . esc_attr($nonce) . '" />';
        if ($echo) {
            echo $output;
        }
        return $output;
    }
}

// Mock selected
if (!function_exists('selected')) {
    function selected($selected, $current = true, $echo = true) {
        $result = '';
        if ((string) $selected === (string) $current) {
            $result = ' selected="selected"';
        }
        if ($echo) {
            echo $result;
        }
        return $result;
    }
}

// Mock checked
if (!function_exists('checked')) {
    function checked($checked, $current = true, $echo = true) {
        $result = '';
        if ((string) $checked === (string) $current) {
            $result = ' checked="checked"';
        }
        if ($echo) {
            echo $result;
        }
        return $result;
    }
}

// Mock disabled
if (!function_exists('disabled')) {
    function disabled($disabled, $current = true, $echo = true) {
        $result = '';
        if ((string) $disabled === (string) $current) {
            $result = ' disabled="disabled"';
        }
        if ($echo) {
            echo $result;
        }
        return $result;
    }
}

// Mock add_meta_box - removed duplicate, see line 860 for actual implementation

// Mock add_menu_page - removed duplicate, see line 864 for actual implementation

// Mock add_submenu_page - removed duplicate, see line 862 for actual implementation

// Mock settings_fields
if (!function_exists('settings_fields')) {
    function settings_fields($option_group) {
        echo '<input type="hidden" name="option_page" value="' . esc_attr($option_group) . '" />';
    }
}

// Mock do_settings_sections
if (!function_exists('do_settings_sections')) {
    function do_settings_sections($page) {
        // No-op for testing
    }
}

// Mock submit_button
if (!function_exists('submit_button')) {
    function submit_button($text = null, $type = 'primary', $name = 'submit', $wrap = true, $other_attributes = null) {
        echo '<button type="submit" name="' . esc_attr($name) . '">' . esc_html($text ?: 'Submit') . '</button>';
    }
}

// Mock get_admin_page_title
if (!function_exists('get_admin_page_title')) {
    function get_admin_page_title() {
        return 'Schema Validator Pro';
    }
}

// Mock register_setting - removed duplicate, see line 857 for actual implementation

// Mock add_settings_section
if (!function_exists('add_settings_section')) {
    function add_settings_section($id, $title, $callback, $page) {
        // No-op for testing
    }
}

// Mock add_settings_field
if (!function_exists('add_settings_field')) {
    function add_settings_field($id, $title, $callback, $page, $section = 'default', $args = []) {
        // No-op for testing
    }
}

// Mock wp_send_json_success
if (!function_exists('wp_send_json_success')) {
    function wp_send_json_success($data = null, $status_code = null) {
        echo json_encode(['success' => true, 'data' => $data]);
        exit;
    }
}

// Mock wp_send_json_error
if (!function_exists('wp_send_json_error')) {
    function wp_send_json_error($data = null, $status_code = null) {
        echo json_encode(['success' => false, 'data' => $data]);
        exit;
    }
}

// Mock get_the_author_meta
if (!function_exists('get_the_author_meta')) {
    function get_the_author_meta($field = '', $user_id = false) {
        return 'Test Author';
    }
}

// Mock get_the_date
if (!function_exists('get_the_date')) {
    function get_the_date($format = '', $post = null) {
        return date($format ?: 'Y-m-d');
    }
}

// Mock get_permalink
if (!function_exists('get_permalink')) {
    function get_permalink($post = 0) {
        return 'https://example.com/test-post/';
    }
}

// Mock wp_remote_post
if (!function_exists('wp_remote_post')) {
    function wp_remote_post($url, $args = []) {
        global $test_wp_remote_response;
        return $test_wp_remote_response ?? ['body' => '{"schema": {}}', 'response' => ['code' => 200]];
    }
}

// Mock wp_strip_all_tags
if (!function_exists('wp_strip_all_tags')) {
    function wp_strip_all_tags($string, $remove_breaks = false) {
        return strip_tags($string);
    }
}

// Mock sprintf for translations
if (!function_exists('sprintf')) {
    // sprintf is a PHP built-in, this is just a placeholder
}

// Mock wp_remote_get for HTTP requests
if (!function_exists('wp_remote_get')) {
    function wp_remote_get($url, $args = []) {
        global $test_wp_remote_response;
        if (isset($test_wp_remote_response)) {
            return $test_wp_remote_response;
        }
        // Default: return error
        return new WP_Error('http_request_failed', 'Could not connect to API');
    }
}

// Mock wp_remote_retrieve_response_code
if (!function_exists('wp_remote_retrieve_response_code')) {
    function wp_remote_retrieve_response_code($response) {
        if (is_wp_error($response)) {
            return 0;
        }
        return isset($response['response']['code']) ? $response['response']['code'] : 200;
    }
}

// Mock wp_remote_retrieve_body
if (!function_exists('wp_remote_retrieve_body')) {
    function wp_remote_retrieve_body($response) {
        if (is_wp_error($response)) {
            return '';
        }
        return isset($response['body']) ? $response['body'] : '';
    }
}

// Mock is_wp_error
if (!function_exists('is_wp_error')) {
    function is_wp_error($thing) {
        return ($thing instanceof WP_Error);
    }
}

// Mock WP_Error class
if (!class_exists('WP_Error')) {
    class WP_Error {
        private $errors = [];
        private $error_data = [];

        public function __construct($code = '', $message = '', $data = '') {
            if (empty($code)) {
                return;
            }
            $this->errors[$code][] = $message;
            if (!empty($data)) {
                $this->error_data[$code] = $data;
            }
        }

        public function get_error_code() {
            $codes = array_keys($this->errors);
            return empty($codes) ? '' : $codes[0];
        }

        public function get_error_message($code = '') {
            if (empty($code)) {
                $code = $this->get_error_code();
            }
            if (isset($this->errors[$code])) {
                return $this->errors[$code][0];
            }
            return '';
        }

        public function get_error_messages($code = '') {
            if (empty($code)) {
                $all_messages = [];
                foreach ($this->errors as $code => $messages) {
                    $all_messages = array_merge($all_messages, $messages);
                }
                return $all_messages;
            }
            return isset($this->errors[$code]) ? $this->errors[$code] : [];
        }

        public function add($code, $message, $data = '') {
            $this->errors[$code][] = $message;
            if (!empty($data)) {
                $this->error_data[$code] = $data;
            }
        }
    }
}

// Mock wp_die
if (!function_exists('wp_die')) {
    function wp_die($message = '', $title = '', $args = []) {
        global $test_wp_die_called;
        $test_wp_die_called = true;
        throw new Exception('wp_die called: ' . $message);
    }
}

// Mock current_user_can
if (!function_exists('current_user_can')) {
    function current_user_can($capability, ...$args) {
        global $test_user_can;
        return isset($test_user_can) ? $test_user_can : true;
    }
}

// Mock wpdb class
if (!class_exists('wpdb')) {
    class wpdb {
        public $options = 'wp_options';

        public function query($query) {
            global $test_wpdb_query_result, $test_transients;

            // If this is a DELETE query for SVP transients, also clear $test_transients
            // Note: underscores in query are escaped as \_
            if (strpos($query, 'DELETE') !== false && (strpos($query, 'svp\\_schema\\_') !== false || strpos($query, 'svp_schema_') !== false)) {
                // Extract post_id from query if present
                // Pattern: \_transient\_svp\_schema\_123\_% or svp_schema_123_
                if (preg_match("/svp\\\\_schema\\\\_(\\d+)\\\\_/", $query, $matches) || preg_match("/svp_schema_(\\d+)_/", $query, $matches)) {
                    $post_id = $matches[1];
                    // Clear all transients for this post
                    foreach (array_keys($test_transients) as $key) {
                        if (strpos($key, 'svp_schema_' . $post_id . '_') === 0) {
                            unset($test_transients[$key]);
                        }
                    }
                } else {
                    // Clear all SVP transients
                    foreach (array_keys($test_transients) as $key) {
                        if (strpos($key, 'svp_schema_') === 0) {
                            unset($test_transients[$key]);
                        }
                    }
                }
            }

            return isset($test_wpdb_query_result) ? $test_wpdb_query_result : 0;
        }

        public function prepare($query, ...$args) {
            // Simple mock implementation
            $query = str_replace('%s', "'%s'", $query);
            $query = str_replace('%d', '%d', $query);
            return vsprintf($query, $args);
        }

        public function esc_like($text) {
            return addcslashes($text, '_%\\');
        }
    }
}

// Create global $wpdb instance
global $wpdb;
if (!isset($wpdb)) {
    $wpdb = new wpdb();
}

// Mock esc_url_raw
if (!function_exists('esc_url_raw')) {
    function esc_url_raw($url, $protocols = null) {
        // Simple sanitization for testing
        $url = trim($url);
        if (empty($url)) {
            return '';
        }
        // Block dangerous protocols
        $dangerous = ['javascript:', 'data:', 'vbscript:', 'file:'];
        foreach ($dangerous as $protocol) {
            if (stripos($url, $protocol) === 0) {
                return '';
            }
        }
        // Only allow http and https
        if (!preg_match('/^https?:\/\//i', $url)) {
            return '';
        }
        return $url;
    }
}

// Mock mysql2date
if (!function_exists('mysql2date')) {
    function mysql2date($format, $date, $translate = true) {
        return date($format, strtotime($date));
    }
}

// Mock load_plugin_textdomain
if (!function_exists('load_plugin_textdomain')) {
    function load_plugin_textdomain($domain, $deprecated = false, $plugin_rel_path = false) {
        global $test_load_textdomain_called;
        $test_load_textdomain_called = true;
        return true;
    }
}

// Mock add_menu_page
if (!function_exists('add_menu_page')) {
    function add_menu_page($page_title, $menu_title, $capability, $menu_slug, $callback = '', $icon_url = '', $position = null) {
        global $test_add_menu_page_called;
        $test_add_menu_page_called = true;
        return 'toplevel_page_' . $menu_slug;
    }
}

// Mock add_submenu_page
if (!function_exists('add_submenu_page')) {
    function add_submenu_page($parent_slug, $page_title, $menu_title, $capability, $menu_slug, $callback = '') {
        return $parent_slug . '_page_' . $menu_slug;
    }
}

// Mock register_setting
if (!function_exists('register_setting')) {
    function register_setting($option_group, $option_name, $args = []) {
        global $test_register_setting_called;
        $test_register_setting_called = true;
    }
}

// Mock add_meta_box
if (!function_exists('add_meta_box')) {
    function add_meta_box($id, $title, $callback, $screen = null, $context = 'advanced', $priority = 'default', $callback_args = null) {
        global $test_add_meta_box_called;
        $test_add_meta_box_called = true;
    }
}

// Load the plugin file (but don't execute hooks yet)
// We'll load specific functions in each test file as needed

// Register shutdown function to tear down Brain Monkey
register_shutdown_function(function() {
    \Brain\Monkey\tearDown();
});

