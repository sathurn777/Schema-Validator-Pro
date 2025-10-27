<?php
/**
 * Execution Tests for API Status Checking
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class ApiStatusExecutionTest extends TestCase {

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
        global $test_wp_remote_response;
        $test_wp_remote_response = null;
    }

    /**
     * Test check_api_status with empty endpoint returns unavailable
     */
    public function test_check_api_status_empty_endpoint_returns_unavailable() {
        $result = svp_check_api_status('');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
        $this->assertFalse($result['available']);
        $this->assertArrayHasKey('error', $result);
    }

    /**
     * Test check_api_status with null endpoint returns unavailable
     */
    public function test_check_api_status_null_endpoint_returns_unavailable() {
        $result = svp_check_api_status(null);
        
        $this->assertIsArray($result);
        $this->assertFalse($result['available']);
        $this->assertArrayHasKey('error', $result);
    }

    /**
     * Test check_api_status with valid endpoint and successful response
     */
    public function test_check_api_status_successful_response() {
        global $test_wp_remote_response;
        $test_wp_remote_response = [
            'response' => ['code' => 200],
            'body' => json_encode(['status' => 'ok']),
        ];
        
        $result = svp_check_api_status('http://localhost:8000');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
        $this->assertIsBool($result['available']);
    }

    /**
     * Test check_api_status with network error
     */
    public function test_check_api_status_network_error() {
        global $test_wp_remote_response;
        
        // Create WP_Error mock
        $error = new WP_Error('http_request_failed', 'Network error');
        $test_wp_remote_response = $error;
        
        $result = svp_check_api_status('http://localhost:8000');
        
        $this->assertIsArray($result);
        $this->assertFalse($result['available']);
        $this->assertArrayHasKey('error', $result);
    }

    /**
     * Test check_api_status with 500 error
     */
    public function test_check_api_status_500_error() {
        global $test_wp_remote_response;
        $test_wp_remote_response = [
            'response' => ['code' => 500],
            'body' => 'Internal Server Error',
        ];
        
        $result = svp_check_api_status('http://localhost:8000');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
    }

    /**
     * Test check_api_status with 404 error
     */
    public function test_check_api_status_404_error() {
        global $test_wp_remote_response;
        $test_wp_remote_response = [
            'response' => ['code' => 404],
            'body' => 'Not Found',
        ];
        
        $result = svp_check_api_status('http://localhost:8000');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
    }

    /**
     * Test check_api_status with different endpoints
     */
    public function test_check_api_status_different_endpoints() {
        $endpoints = [
            'http://localhost:8000',
            'https://api.example.com',
            'http://192.168.1.1:3000',
        ];
        
        foreach ($endpoints as $endpoint) {
            $result = svp_check_api_status($endpoint);
            
            $this->assertIsArray($result);
            $this->assertArrayHasKey('available', $result);
        }
    }

    /**
     * Test check_api_status return structure
     */
    public function test_check_api_status_return_structure() {
        $result = svp_check_api_status('http://localhost:8000');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
        
        if (!$result['available']) {
            $this->assertArrayHasKey('error', $result);
        }
    }

    /**
     * Test check_api_status with invalid URL format
     */
    public function test_check_api_status_invalid_url_format() {
        $result = svp_check_api_status('not-a-valid-url');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
    }

    /**
     * Test check_api_status with localhost
     */
    public function test_check_api_status_localhost() {
        $result = svp_check_api_status('http://localhost:8000');
        
        $this->assertIsArray($result);
        $this->assertIsBool($result['available']);
    }

    /**
     * Test check_api_status with https endpoint
     */
    public function test_check_api_status_https_endpoint() {
        $result = svp_check_api_status('https://api.example.com');
        
        $this->assertIsArray($result);
        $this->assertIsBool($result['available']);
    }

    /**
     * Test check_api_status with port number
     */
    public function test_check_api_status_with_port() {
        $result = svp_check_api_status('http://localhost:3000');
        
        $this->assertIsArray($result);
        $this->assertIsBool($result['available']);
    }

    /**
     * Test check_api_status with path
     */
    public function test_check_api_status_with_path() {
        $result = svp_check_api_status('http://localhost:8000/api/v1');
        
        $this->assertIsArray($result);
        $this->assertIsBool($result['available']);
    }

    /**
     * Test check_api_status error message format
     */
    public function test_check_api_status_error_message_format() {
        $result = svp_check_api_status('');
        
        $this->assertArrayHasKey('error', $result);
        $this->assertIsString($result['error']);
        $this->assertNotEmpty($result['error']);
    }

    /**
     * Test check_api_status with very long endpoint
     */
    public function test_check_api_status_long_endpoint() {
        $long_endpoint = 'http://very-long-domain-name-that-is-extremely-long.example.com:8000/api/v1/endpoint';
        $result = svp_check_api_status($long_endpoint);
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
    }

    /**
     * Test check_api_status with special characters in URL
     */
    public function test_check_api_status_special_chars_in_url() {
        $result = svp_check_api_status('http://localhost:8000/api?key=value&test=123');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
    }
}

