<?php
/**
 * Tests for Meta Box Functions
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class MetaBoxTest extends TestCase {

    private static $plugin_loaded = false;

    public static function setUpBeforeClass(): void {
        parent::setUpBeforeClass();
        
        if (!self::$plugin_loaded) {
            require_once dirname(__DIR__) . '/schema-validator-pro.php';
            self::$plugin_loaded = true;
        }
    }

    /**
     * Test svp_add_meta_box function exists
     */
    public function test_add_meta_box_function_exists() {
        $this->assertTrue(function_exists('svp_add_meta_box'));
    }

    /**
     * Test svp_schema_metabox_callback function exists
     */
    public function test_schema_metabox_callback_function_exists() {
        $this->assertTrue(function_exists('svp_schema_metabox_callback'));
    }

    /**
     * Test svp_enqueue_admin_assets function exists
     */
    public function test_enqueue_admin_assets_function_exists() {
        $this->assertTrue(function_exists('svp_enqueue_admin_assets'));
    }

    /**
     * Test svp_enqueue_admin_page_assets function exists
     */
    public function test_enqueue_admin_page_assets_function_exists() {
        $this->assertTrue(function_exists('svp_enqueue_admin_page_assets'));
    }

    /**
     * Test svp_clear_cache_on_post_update function exists
     */
    public function test_clear_cache_on_post_update_function_exists() {
        $this->assertTrue(function_exists('svp_clear_cache_on_post_update'));
    }

    /**
     * Test svp_inject_schema function exists
     */
    public function test_inject_schema_function_exists() {
        $this->assertTrue(function_exists('svp_inject_schema'));
    }

    /**
     * Test svp_has_existing_schema function exists
     */
    public function test_has_existing_schema_function_exists() {
        $this->assertTrue(function_exists('svp_has_existing_schema'));
    }
}

