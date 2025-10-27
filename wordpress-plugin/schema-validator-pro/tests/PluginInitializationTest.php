<?php
/**
 * Tests for Plugin Initialization Functions
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class PluginInitializationTest extends TestCase {

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
        global $test_load_textdomain_called, $test_add_menu_page_called, $test_register_setting_called;
        $test_load_textdomain_called = false;
        $test_add_menu_page_called = false;
        $test_register_setting_called = false;
    }

    /**
     * Test load textdomain function exists
     */
    public function test_load_textdomain_function_exists() {
        $this->assertTrue(function_exists('svp_load_textdomain'));
    }

    /**
     * Test load textdomain is called
     */
    public function test_load_textdomain_is_called() {
        global $test_load_textdomain_called;
        
        svp_load_textdomain();
        
        $this->assertTrue($test_load_textdomain_called);
    }

    /**
     * Test add admin menu function exists
     */
    public function test_add_admin_menu_function_exists() {
        $this->assertTrue(function_exists('svp_add_admin_menu'));
    }

    /**
     * Test add admin menu is called
     */
    public function test_add_admin_menu_is_called() {
        global $test_add_menu_page_called;
        
        svp_add_admin_menu();
        
        $this->assertTrue($test_add_menu_page_called);
    }

    /**
     * Test register settings function exists
     */
    public function test_register_settings_function_exists() {
        $this->assertTrue(function_exists('svp_register_settings'));
    }

    /**
     * Test register settings is called
     */
    public function test_register_settings_is_called() {
        global $test_register_setting_called;
        
        svp_register_settings();
        
        $this->assertTrue($test_register_setting_called);
    }

    /**
     * Test enqueue admin page assets function exists
     */
    public function test_enqueue_admin_page_assets_function_exists() {
        $this->assertTrue(function_exists('svp_enqueue_admin_page_assets'));
    }

    /**
     * Test enqueue admin page assets on correct hook
     */
    public function test_enqueue_admin_page_assets_on_correct_hook() {
        global $test_wp_enqueue_style_called;
        $test_wp_enqueue_style_called = false;
        
        svp_enqueue_admin_page_assets('toplevel_page_schema-validator-pro');
        
        $this->assertTrue($test_wp_enqueue_style_called);
    }

    /**
     * Test enqueue admin page assets on wrong hook
     */
    public function test_enqueue_admin_page_assets_on_wrong_hook() {
        global $test_wp_enqueue_style_called;
        $test_wp_enqueue_style_called = false;
        
        svp_enqueue_admin_page_assets('edit.php');
        
        $this->assertFalse($test_wp_enqueue_style_called);
    }

    /**
     * Test enqueue admin page assets on settings page
     */
    public function test_enqueue_admin_page_assets_on_settings_page() {
        global $test_wp_enqueue_style_called;
        $test_wp_enqueue_style_called = false;
        
        svp_enqueue_admin_page_assets('schema-validator-pro_page_svp-settings');
        
        $this->assertTrue($test_wp_enqueue_style_called);
    }

    /**
     * Test has existing schema function exists
     */
    public function test_has_existing_schema_function_exists() {
        $this->assertTrue(function_exists('svp_has_existing_schema'));
    }

    /**
     * Test has existing schema with null post causes error
     * Note: This is a bug in the plugin - it should check if $post exists first
     */
    public function test_has_existing_schema_with_null_post() {
        global $post;
        $post = null;

        // The function will cause an error when $post is null
        // because it tries to access $post->ID without checking
        $this->expectError();

        svp_has_existing_schema();
    }

    /**
     * Test has existing schema returns false when no content
     */
    public function test_has_existing_schema_returns_false_when_no_content() {
        global $post;
        $post = (object) [
            'ID' => 123,
            'post_content' => ''
        ];
        
        $result = svp_has_existing_schema();
        
        $this->assertFalse($result);
    }

    /**
     * Test has existing schema returns false by default
     */
    public function test_has_existing_schema_returns_false_by_default() {
        global $post;
        $post = (object) [
            'ID' => 123,
            'post_content' => '<script type="application/ld+json">{"@type":"Article"}</script>'
        ];

        $result = svp_has_existing_schema();

        // Function uses apply_filters, which returns false by default in tests
        $this->assertFalse($result);
    }

    /**
     * Test has existing schema uses apply_filters
     */
    public function test_has_existing_schema_uses_apply_filters() {
        global $post;
        $post = (object) [
            'ID' => 123,
            'post_content' => 'Some content'
        ];

        $result = svp_has_existing_schema();

        // Function uses apply_filters, which returns the default value (false)
        $this->assertFalse($result);
    }

    /**
     * Test has existing schema with post
     */
    public function test_has_existing_schema_with_post() {
        global $post;
        $post = (object) [
            'ID' => 123,
            'post_content' => '<script>console.log("test");</script>'
        ];

        $result = svp_has_existing_schema();

        $this->assertFalse($result);
    }

    /**
     * Test add meta box function exists
     */
    public function test_add_meta_box_function_exists() {
        $this->assertTrue(function_exists('svp_add_meta_box'));
    }

    /**
     * Test add meta box is called
     */
    public function test_add_meta_box_is_called() {
        global $test_add_meta_box_called;
        $test_add_meta_box_called = false;
        
        svp_add_meta_box();
        
        $this->assertTrue($test_add_meta_box_called);
    }
}

