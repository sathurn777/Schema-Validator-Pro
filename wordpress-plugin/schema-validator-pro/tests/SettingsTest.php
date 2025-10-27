<?php
/**
 * Tests for Settings Functions
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class SettingsTest extends TestCase {

    private static $plugin_loaded = false;

    public static function setUpBeforeClass(): void {
        parent::setUpBeforeClass();
        
        if (!self::$plugin_loaded) {
            require_once dirname(__DIR__) . '/schema-validator-pro.php';
            self::$plugin_loaded = true;
        }
    }

    /**
     * Test svp_register_settings function exists
     */
    public function test_register_settings_function_exists() {
        $this->assertTrue(function_exists('svp_register_settings'));
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
     * Test svp_add_admin_menu function exists
     */
    public function test_add_admin_menu_function_exists() {
        $this->assertTrue(function_exists('svp_add_admin_menu'));
    }

    /**
     * Test svp_load_textdomain function exists
     */
    public function test_load_textdomain_function_exists() {
        $this->assertTrue(function_exists('svp_load_textdomain'));
    }

    /**
     * Test plugin constants are defined
     */
    public function test_plugin_constants_defined() {
        $this->assertTrue(defined('SCHEMA_VALIDATOR_PRO_VERSION'));
        $this->assertTrue(defined('SCHEMA_VALIDATOR_PRO_FILE'));
        $this->assertTrue(defined('SCHEMA_VALIDATOR_PRO_DIR'));
        $this->assertTrue(defined('SCHEMA_VALIDATOR_PRO_URL'));
    }

    /**
     * Test plugin version format
     */
    public function test_plugin_version_format() {
        $version = SCHEMA_VALIDATOR_PRO_VERSION;

        $this->assertMatchesRegularExpression('/^\d+\.\d+\.\d+$/', $version);
    }

    /**
     * Test plugin file path
     */
    public function test_plugin_file_path() {
        $file = SCHEMA_VALIDATOR_PRO_FILE;

        $this->assertIsString($file);
        $this->assertNotEmpty($file);
    }

    /**
     * Test plugin directory path
     */
    public function test_plugin_directory_path() {
        $dir = SCHEMA_VALIDATOR_PRO_DIR;

        $this->assertIsString($dir);
        $this->assertNotEmpty($dir);
    }

    /**
     * Test plugin URL
     */
    public function test_plugin_url() {
        $url = SCHEMA_VALIDATOR_PRO_URL;

        $this->assertIsString($url);
        $this->assertNotEmpty($url);
    }
}

