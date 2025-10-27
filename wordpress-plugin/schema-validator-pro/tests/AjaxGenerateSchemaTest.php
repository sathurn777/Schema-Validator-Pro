<?php
/**
 * Tests for AJAX Schema Generation
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class AjaxGenerateSchemaTest extends TestCase {

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
        global $_POST, $test_post_meta, $test_transients, $test_wp_remote_response, $test_options;
        $_POST = [];
        $test_post_meta = [];
        $test_transients = [];
        $test_wp_remote_response = null;
        $test_options = [];
    }

    /**
     * Test AJAX with invalid post ID returns error
     */
    public function test_ajax_invalid_post_id_returns_error() {
        global $_POST, $test_ajax_response;
        $_POST['post_id'] = 0;
        $test_ajax_response = null;
        
        svp_ajax_generate_schema();
        
        $this->assertNotNull($test_ajax_response);
        $this->assertFalse($test_ajax_response['success']);
    }

    /**
     * Test AJAX with missing post ID returns error
     */
    public function test_ajax_missing_post_id_returns_error() {
        global $test_ajax_response;
        $test_ajax_response = null;
        
        svp_ajax_generate_schema();
        
        $this->assertNotNull($test_ajax_response);
        $this->assertFalse($test_ajax_response['success']);
    }

    /**
     * Test AJAX with valid post ID but no permissions
     */
    public function test_ajax_no_permissions_returns_error() {
        global $_POST, $test_ajax_response, $test_user_can;
        $_POST['post_id'] = 123;
        $test_user_can = false;
        $test_ajax_response = null;
        
        svp_ajax_generate_schema();
        
        $this->assertNotNull($test_ajax_response);
        $this->assertFalse($test_ajax_response['success']);
    }

    /**
     * Test AJAX with non-existent post
     */
    public function test_ajax_post_not_found_returns_error() {
        global $_POST, $test_ajax_response, $test_user_can, $test_get_post;
        $_POST['post_id'] = 999;
        $test_user_can = true;
        $test_get_post = null;
        $test_ajax_response = null;
        
        svp_ajax_generate_schema();
        
        $this->assertNotNull($test_ajax_response);
        $this->assertFalse($test_ajax_response['success']);
    }

    /**
     * Test AJAX returns cached schema when available
     */
    public function test_ajax_returns_cached_schema() {
        global $_POST, $test_ajax_response, $test_user_can, $test_get_post, $test_transients;
        
        $_POST['post_id'] = 123;
        $_POST['schema_type'] = 'Article';
        $test_user_can = true;
        $test_get_post = (object) [
            'ID' => 123,
            'post_title' => 'Test',
            'post_content' => 'Content',
            'post_author' => 1,
        ];
        
        $cached_schema = ['@type' => 'Article', 'headline' => 'Cached'];
        $cache_key = svp_get_schema_cache_key(123, 'Article');
        $test_transients[$cache_key] = $cached_schema;
        $test_ajax_response = null;
        
        svp_ajax_generate_schema();
        
        $this->assertNotNull($test_ajax_response);
        $this->assertTrue($test_ajax_response['success']);
        $this->assertTrue($test_ajax_response['data']['cached']);
    }

    /**
     * Test AJAX with force regenerate bypasses cache
     */
    public function test_ajax_force_regenerate_bypasses_cache() {
        global $_POST, $test_ajax_response, $test_user_can, $test_get_post, $test_transients, $test_options;
        
        $_POST['post_id'] = 123;
        $_POST['schema_type'] = 'Article';
        $_POST['force'] = 'true';
        $test_user_can = true;
        $test_get_post = (object) [
            'ID' => 123,
            'post_title' => 'Test',
            'post_content' => 'Content',
            'post_author' => 1,
        ];
        
        // Set cached schema
        $cache_key = svp_get_schema_cache_key(123, 'Article');
        $test_transients[$cache_key] = ['@type' => 'Article', 'headline' => 'Cached'];
        
        // Set API endpoint to empty to trigger error
        $test_options['svp_api_endpoint'] = '';
        $test_ajax_response = null;
        
        svp_ajax_generate_schema();
        
        // Should not use cache, should error because no API
        $this->assertNotNull($test_ajax_response);
    }

    /**
     * Test AJAX with empty API endpoint returns error
     */
    public function test_ajax_empty_api_endpoint_returns_error() {
        global $_POST, $test_ajax_response, $test_user_can, $test_get_post, $test_options;
        
        $_POST['post_id'] = 123;
        $_POST['schema_type'] = 'Article';
        $_POST['force'] = 'true';
        $test_user_can = true;
        $test_get_post = (object) [
            'ID' => 123,
            'post_title' => 'Test',
            'post_content' => 'Content',
            'post_author' => 1,
        ];
        $test_options['svp_api_endpoint'] = '';
        $test_ajax_response = null;
        
        svp_ajax_generate_schema();
        
        $this->assertNotNull($test_ajax_response);
        $this->assertFalse($test_ajax_response['success']);
    }

    /**
     * Test AJAX with API network error falls back to cache
     */
    public function test_ajax_network_error_falls_back_to_cache() {
        global $_POST, $test_ajax_response, $test_user_can, $test_get_post, $test_options, $test_transients, $test_wp_remote_response;
        
        $_POST['post_id'] = 123;
        $_POST['schema_type'] = 'Article';
        $_POST['force'] = 'true';
        $test_user_can = true;
        $test_get_post = (object) [
            'ID' => 123,
            'post_title' => 'Test',
            'post_content' => 'Content',
            'post_author' => 1,
        ];
        $test_options['svp_api_endpoint'] = 'http://localhost:8000';
        
        // Set cached schema
        $cache_key = svp_get_schema_cache_key(123, 'Article');
        $test_transients[$cache_key] = ['@type' => 'Article', 'headline' => 'Cached'];
        
        // Simulate network error
        $test_wp_remote_response = new WP_Error('http_request_failed', 'Network error');
        $test_ajax_response = null;
        
        svp_ajax_generate_schema();
        
        $this->assertNotNull($test_ajax_response);
        $this->assertTrue($test_ajax_response['success']);
        $this->assertTrue($test_ajax_response['data']['cached']);
        $this->assertTrue($test_ajax_response['data']['fallback']);
    }

    /**
     * Test AJAX with API 500 error falls back to cache
     */
    public function test_ajax_500_error_falls_back_to_cache() {
        global $_POST, $test_ajax_response, $test_user_can, $test_get_post, $test_options, $test_transients, $test_wp_remote_response;
        
        $_POST['post_id'] = 123;
        $_POST['schema_type'] = 'Article';
        $_POST['force'] = 'true';
        $test_user_can = true;
        $test_get_post = (object) [
            'ID' => 123,
            'post_title' => 'Test',
            'post_content' => 'Content',
            'post_author' => 1,
        ];
        $test_options['svp_api_endpoint'] = 'http://localhost:8000';
        
        // Set cached schema
        $cache_key = svp_get_schema_cache_key(123, 'Article');
        $test_transients[$cache_key] = ['@type' => 'Article', 'headline' => 'Cached'];
        
        // Simulate 500 error
        $test_wp_remote_response = [
            'response' => ['code' => 500],
            'body' => 'Internal Server Error',
        ];
        $test_ajax_response = null;
        
        svp_ajax_generate_schema();
        
        $this->assertNotNull($test_ajax_response);
        $this->assertTrue($test_ajax_response['success']);
        $this->assertTrue($test_ajax_response['data']['cached']);
        $this->assertTrue($test_ajax_response['data']['fallback']);
    }

    /**
     * Test AJAX with API 404 error returns error
     */
    public function test_ajax_404_error_returns_error() {
        global $_POST, $test_ajax_response, $test_user_can, $test_get_post, $test_options, $test_wp_remote_response;
        
        $_POST['post_id'] = 123;
        $_POST['schema_type'] = 'Article';
        $_POST['force'] = 'true';
        $test_user_can = true;
        $test_get_post = (object) [
            'ID' => 123,
            'post_title' => 'Test',
            'post_content' => 'Content',
            'post_author' => 1,
        ];
        $test_options['svp_api_endpoint'] = 'http://localhost:8000';
        
        // Simulate 404 error
        $test_wp_remote_response = [
            'response' => ['code' => 404],
            'body' => json_encode(['detail' => 'Not found']),
        ];
        $test_ajax_response = null;
        
        svp_ajax_generate_schema();
        
        $this->assertNotNull($test_ajax_response);
        $this->assertFalse($test_ajax_response['success']);
    }

    /**
     * Test AJAX with successful API response
     */
    public function test_ajax_successful_api_response() {
        global $_POST, $test_ajax_response, $test_user_can, $test_get_post, $test_options, $test_wp_remote_response, $test_post_meta, $test_transients;

        $_POST['post_id'] = 123;
        $_POST['schema_type'] = 'Article';
        $_POST['force'] = 'true';
        $test_user_can = true;
        $test_get_post = (object) [
            'ID' => 123,
            'post_title' => 'Test Article',
            'post_content' => 'Test content',
            'post_author' => 1,
        ];
        $test_options['svp_api_endpoint'] = 'http://localhost:8000';
        $test_post_meta = [123 => []];
        $test_transients = []; // Clear cache

        // Simulate successful API response
        $schema = [
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => 'Test Article',
        ];
        $test_wp_remote_response = [
            'response' => ['code' => 200],
            'body' => json_encode(['schema' => $schema]),
        ];
        $test_ajax_response = null;

        svp_ajax_generate_schema();

        $this->assertNotNull($test_ajax_response);
        if (!$test_ajax_response['success']) {
            // Debug: print the error
            var_dump($test_ajax_response);
        }
        $this->assertTrue($test_ajax_response['success']);
        $this->assertFalse($test_ajax_response['data']['cached']);
        $this->assertArrayHasKey('schema', $test_ajax_response['data']);
    }
}

