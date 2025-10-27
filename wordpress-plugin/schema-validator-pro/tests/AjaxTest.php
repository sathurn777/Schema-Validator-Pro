<?php
/**
 * Tests for AJAX Handler Functions
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class AjaxTest extends TestCase {

    private static $plugin_loaded = false;

    public static function setUpBeforeClass(): void {
        parent::setUpBeforeClass();
        
        if (!self::$plugin_loaded) {
            require_once dirname(__DIR__) . '/schema-validator-pro.php';
            self::$plugin_loaded = true;
        }
    }

    /**
     * Test svp_ajax_generate_schema function exists
     */
    public function test_ajax_generate_schema_function_exists() {
        $this->assertTrue(function_exists('svp_ajax_generate_schema'));
    }

    /**
     * Test svp_logger function exists
     */
    public function test_logger_function_exists() {
        $this->assertTrue(function_exists('svp_logger'));
    }

    /**
     * Test logger returns SVP_Logger instance
     */
    public function test_logger_returns_instance() {
        $logger = svp_logger();
        
        $this->assertInstanceOf(SVP_Logger::class, $logger);
    }

    /**
     * Test logger singleton pattern
     */
    public function test_logger_singleton() {
        $logger1 = svp_logger();
        $logger2 = svp_logger();
        
        $this->assertSame($logger1, $logger2);
    }

    /**
     * Test svp_check_api_status function exists
     */
    public function test_check_api_status_function_exists() {
        $this->assertTrue(function_exists('svp_check_api_status'));
    }

    /**
     * Test API status check with empty endpoint
     */
    public function test_api_status_empty_endpoint() {
        $result = svp_check_api_status('');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
        $this->assertFalse($result['available']);
    }

    /**
     * Test API status check with null endpoint
     */
    public function test_api_status_null_endpoint() {
        $result = svp_check_api_status(null);
        
        $this->assertIsArray($result);
        $this->assertFalse($result['available']);
    }

    /**
     * Test API status check returns array
     */
    public function test_api_status_returns_array() {
        $result = svp_check_api_status('http://localhost:8000');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
    }

    /**
     * Test API status check with invalid URL
     */
    public function test_api_status_invalid_url() {
        $result = svp_check_api_status('not-a-url');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
    }

    /**
     * Test API status check with localhost
     */
    public function test_api_status_localhost() {
        $result = svp_check_api_status('http://localhost:8000');
        
        $this->assertIsArray($result);
        $this->assertIsBool($result['available']);
    }

    /**
     * Test API status check structure
     */
    public function test_api_status_structure() {
        $result = svp_check_api_status('http://localhost:8000');
        
        $this->assertIsArray($result);
        $this->assertArrayHasKey('available', $result);
        
        if (!$result['available']) {
            $this->assertArrayHasKey('error', $result);
        }
    }

    /**
     * Test svp_settings_page function exists
     */
    public function test_settings_page_function_exists() {
        $this->assertTrue(function_exists('svp_settings_page'));
    }

    /**
     * Test svp_admin_page function exists
     */
    public function test_admin_page_function_exists() {
        $this->assertTrue(function_exists('svp_admin_page'));
    }

    /**
     * Test svp_load_textdomain function exists
     */
    public function test_load_textdomain_function_exists() {
        $this->assertTrue(function_exists('svp_load_textdomain'));
    }
}

