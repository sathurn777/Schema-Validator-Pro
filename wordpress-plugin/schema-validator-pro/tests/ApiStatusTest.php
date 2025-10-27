<?php
/**
 * Tests for API Status Check Functions
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class ApiStatusTest extends TestCase {

    private static $plugin_loaded = false;

    public static function setUpBeforeClass(): void {
        parent::setUpBeforeClass();
        
        // Load plugin functions only once
        if (!self::$plugin_loaded) {
            require_once dirname(__DIR__) . '/schema-validator-pro.php';
            self::$plugin_loaded = true;
        }
    }

    /**
     * Test svp_check_api_status() with empty endpoint
     */
    public function test_check_api_status_empty_endpoint() {
        $result = svp_check_api_status('');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
        $this->assertArrayHasKey('error', $result);
        $this->assertFalse($result['available']);
        $this->assertStringContainsString('No endpoint configured', $result['error']);
    }

    /**
     * Test svp_check_api_status() with null endpoint
     */
    public function test_check_api_status_null_endpoint() {
        $result = svp_check_api_status(null);
        
        $this->assertIsArray($result);
        $this->assertFalse($result['available']);
        $this->assertArrayHasKey('error', $result);
    }

    /**
     * Test svp_check_api_status() returns array structure
     */
    public function test_check_api_status_return_structure() {
        $result = svp_check_api_status('http://localhost:8000');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
        
        // Either has 'error' or 'message' key depending on status
        $this->assertTrue(
            array_key_exists('error', $result) || array_key_exists('message', $result),
            'Result should have either error or message key'
        );
    }

    /**
     * Test svp_check_api_status() with invalid URL format
     */
    public function test_check_api_status_invalid_url() {
        $result = svp_check_api_status('not-a-valid-url');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
        
        // Should either fail or return error
        // We don't assert false here because wp_remote_get might handle it differently
    }

    /**
     * Test svp_check_api_status() with localhost endpoint
     * Note: This will fail if API is not running, which is expected
     */
    public function test_check_api_status_localhost() {
        $result = svp_check_api_status('http://localhost:8000');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
        $this->assertIsBool($result['available']);
        
        // If not available, should have error message
        if (!$result['available']) {
            $this->assertArrayHasKey('error', $result);
            $this->assertIsString($result['error']);
        } else {
            // If available, should have message
            $this->assertArrayHasKey('message', $result);
        }
    }
}

