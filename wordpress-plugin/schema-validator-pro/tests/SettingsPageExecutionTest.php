<?php
/**
 * Execution Tests for Settings Page
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class SettingsPageExecutionTest extends TestCase {

    private static $plugin_loaded = false;

    public static function setUpBeforeClass(): void {
        parent::setUpBeforeClass();
        
        if (!self::$plugin_loaded) {
            require_once dirname(__DIR__) . '/schema-validator-pro.php';
            self::$plugin_loaded = true;
        }
    }

    protected function setUp(): void {
        parent::setUp();
        
        // Clear globals
        global $_POST, $test_options, $test_user_can, $test_wpdb_query_result;
        $_POST = [];
        $test_options = [];
        $test_user_can = true;
        $test_wpdb_query_result = 0;
    }

    /**
     * Test settings page requires manage_options capability
     */
    public function test_settings_page_requires_manage_options() {
        global $test_user_can, $test_wp_die_called;
        $test_user_can = false;
        $test_wp_die_called = false;

        $this->expectException(Exception::class);
        $this->expectExceptionMessage('wp_die called');

        svp_settings_page();
    }

    /**
     * Test settings page renders with manage_options capability
     */
    public function test_settings_page_renders_with_capability() {
        global $test_user_can;
        $test_user_can = true;
        
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertNotEmpty($output);
        $this->assertStringContainsString('svp-settings-page', $output);
    }

    /**
     * Test settings page includes API endpoint field
     */
    public function test_settings_page_includes_api_endpoint_field() {
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('svp_api_endpoint', $output);
        $this->assertStringContainsString('API Endpoint', $output);
    }

    /**
     * Test settings page includes API key field
     */
    public function test_settings_page_includes_api_key_field() {
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('svp_api_key', $output);
        $this->assertStringContainsString('API Key', $output);
    }

    /**
     * Test settings page includes save button
     */
    public function test_settings_page_includes_save_button() {
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('svp_settings_submit', $output);
    }

    /**
     * Test settings page includes clear cache button
     */
    public function test_settings_page_includes_clear_cache_button() {
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('svp_clear_cache', $output);
        $this->assertStringContainsString('Clear All Cache', $output);
    }

    /**
     * Test settings page includes API status section
     */
    public function test_settings_page_includes_api_status() {
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('API Status', $output);
    }

    /**
     * Test settings page saves API endpoint
     */
    public function test_settings_page_saves_api_endpoint() {
        global $_POST, $test_options;

        $_POST['svp_settings_submit'] = '1';
        $_POST['svp_api_endpoint'] = 'http://example.com:8000';
        $_POST['svp_settings_nonce'] = wp_create_nonce('svp_settings_action');

        ob_start();
        svp_settings_page();
        $output = ob_get_clean();

        $this->assertEquals('http://example.com:8000', $test_options['svp_api_endpoint'] ?? '');
        $this->assertStringContainsString('Settings saved successfully', $output);
    }

    /**
     * Test settings page saves API key
     */
    public function test_settings_page_saves_api_key() {
        global $_POST, $test_options;

        $_POST['svp_settings_submit'] = '1';
        $_POST['svp_api_endpoint'] = 'http://localhost:8000';
        $_POST['svp_api_key'] = 'test_api_key_123';
        $_POST['svp_settings_nonce'] = wp_create_nonce('svp_settings_action');

        ob_start();
        svp_settings_page();
        $output = ob_get_clean();

        $this->assertEquals('test_api_key_123', $test_options['svp_api_key'] ?? '');
    }

    /**
     * Test settings page sanitizes API endpoint
     */
    public function test_settings_page_sanitizes_api_endpoint() {
        global $_POST, $test_options;

        $_POST['svp_settings_submit'] = '1';
        $_POST['svp_api_endpoint'] = 'javascript:alert(1)';
        $_POST['svp_settings_nonce'] = wp_create_nonce('svp_settings_action');

        ob_start();
        svp_settings_page();
        ob_end_clean();

        // esc_url_raw should sanitize this
        $this->assertNotEquals('javascript:alert(1)', $test_options['svp_api_endpoint'] ?? '');
    }

    /**
     * Test settings page clears cache
     */
    public function test_settings_page_clears_cache() {
        global $_POST, $test_wpdb_query_result;
        
        $_POST['svp_clear_cache'] = '1';
        $_POST['svp_clear_cache_nonce'] = wp_create_nonce('svp_clear_cache_action');
        $test_wpdb_query_result = 42;
        
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('Cache cleared successfully', $output);
        $this->assertStringContainsString('42', $output);
    }

    /**
     * Test settings page displays current endpoint value
     */
    public function test_settings_page_displays_current_endpoint() {
        global $test_options;
        $test_options['svp_api_endpoint'] = 'http://test.example.com';
        
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('http://test.example.com', $output);
    }

    /**
     * Test settings page displays current API key value
     */
    public function test_settings_page_displays_current_api_key() {
        global $test_options;
        $test_options['svp_api_key'] = 'my_secret_key';
        
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('my_secret_key', $output);
    }

    /**
     * Test settings page shows API available status
     */
    public function test_settings_page_shows_api_available() {
        global $test_options, $test_wp_remote_response;
        $test_options['svp_api_endpoint'] = 'http://localhost:8000';
        $test_wp_remote_response = [
            'response' => ['code' => 200],
            'body' => 'OK',
        ];
        
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('API is available', $output);
    }

    /**
     * Test settings page shows API unavailable status
     */
    public function test_settings_page_shows_api_unavailable() {
        global $test_options, $test_wp_remote_response;
        $test_options['svp_api_endpoint'] = 'http://localhost:8000';
        $test_wp_remote_response = new WP_Error('http_request_failed', 'Could not connect to API');

        ob_start();
        svp_settings_page();
        $output = ob_get_clean();

        $this->assertStringContainsString('API is not available', $output);
        $this->assertStringContainsString('Could not connect to API', $output);
    }

    /**
     * Test settings page with empty endpoint shows default
     */
    public function test_settings_page_with_empty_endpoint_shows_default() {
        global $test_options;
        $test_options = [];
        
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('http://localhost:8000', $output);
    }

    /**
     * Test settings page includes nonce fields
     */
    public function test_settings_page_includes_nonce_fields() {
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('svp_settings_nonce', $output);
        $this->assertStringContainsString('svp_clear_cache_nonce', $output);
    }

    /**
     * Test settings page includes form elements
     */
    public function test_settings_page_includes_form_elements() {
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('<form', $output);
        $this->assertStringContainsString('method="post"', $output);
        $this->assertStringContainsString('<input', $output);
    }

    /**
     * Test settings page includes cache management section
     */
    public function test_settings_page_includes_cache_management() {
        ob_start();
        svp_settings_page();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('Cache Management', $output);
    }

    /**
     * Test settings page with both saves
     */
    public function test_settings_page_saves_both_fields() {
        global $_POST, $test_options;

        $_POST['svp_settings_submit'] = '1';
        $_POST['svp_api_endpoint'] = 'https://api.production.com';
        $_POST['svp_api_key'] = 'prod_key_456';
        $_POST['svp_settings_nonce'] = wp_create_nonce('svp_settings_action');

        ob_start();
        svp_settings_page();
        ob_end_clean();

        $this->assertEquals('https://api.production.com', $test_options['svp_api_endpoint'] ?? '');
        $this->assertEquals('prod_key_456', $test_options['svp_api_key'] ?? '');
    }
}

