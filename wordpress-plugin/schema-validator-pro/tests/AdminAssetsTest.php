<?php
/**
 * Tests for Admin Assets Functions
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class AdminAssetsTest extends TestCase {

    private static $plugin_loaded = false;

    public static function setUpBeforeClass(): void {
        parent::setUpBeforeClass();
        
        if (!self::$plugin_loaded) {
            require_once dirname(__DIR__) . '/schema-validator-pro.php';
            self::$plugin_loaded = true;
        }
    }

    /**
     * Test svp_enqueue_admin_assets exists
     */
    public function test_enqueue_admin_assets_function_exists() {
        $this->assertTrue(function_exists('svp_enqueue_admin_assets'));
    }

    /**
     * Test svp_enqueue_admin_page_assets exists
     */
    public function test_enqueue_admin_page_assets_function_exists() {
        $this->assertTrue(function_exists('svp_enqueue_admin_page_assets'));
    }

    /**
     * Test svp_add_meta_box exists
     */
    public function test_add_meta_box_function_exists() {
        $this->assertTrue(function_exists('svp_add_meta_box'));
    }

    /**
     * Test svp_schema_metabox_callback exists
     */
    public function test_schema_metabox_callback_function_exists() {
        $this->assertTrue(function_exists('svp_schema_metabox_callback'));
    }

    /**
     * Test svp_add_admin_menu exists
     */
    public function test_add_admin_menu_function_exists() {
        $this->assertTrue(function_exists('svp_add_admin_menu'));
    }

    /**
     * Test svp_register_settings exists
     */
    public function test_register_settings_function_exists() {
        $this->assertTrue(function_exists('svp_register_settings'));
    }
}

