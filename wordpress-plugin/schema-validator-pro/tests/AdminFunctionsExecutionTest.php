<?php
/**
 * Execution Tests for Admin Functions
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class AdminFunctionsExecutionTest extends TestCase {

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
        global $post, $test_enqueued_scripts, $test_enqueued_styles;
        $post = null;
        $test_enqueued_scripts = [];
        $test_enqueued_styles = [];
    }

    /**
     * Test enqueue admin assets returns early on non-post screens
     */
    public function test_enqueue_admin_assets_returns_early_on_non_post_screens() {
        global $test_enqueued_scripts, $test_enqueued_styles;
        
        svp_enqueue_admin_assets('index.php');
        
        $this->assertEmpty($test_enqueued_scripts);
        $this->assertEmpty($test_enqueued_styles);
    }

    /**
     * Test enqueue admin assets on post.php
     */
    public function test_enqueue_admin_assets_on_post_edit_screen() {
        global $test_enqueued_scripts, $test_enqueued_styles, $post;
        $post = (object) ['ID' => 123];
        
        svp_enqueue_admin_assets('post.php');
        
        $this->assertNotEmpty($test_enqueued_styles);
        $this->assertNotEmpty($test_enqueued_scripts);
    }

    /**
     * Test enqueue admin assets on post-new.php
     */
    public function test_enqueue_admin_assets_on_post_new_screen() {
        global $test_enqueued_scripts, $test_enqueued_styles, $post;
        $post = (object) ['ID' => 0];
        
        svp_enqueue_admin_assets('post-new.php');
        
        $this->assertNotEmpty($test_enqueued_styles);
        $this->assertNotEmpty($test_enqueued_scripts);
    }

    /**
     * Test enqueue admin assets enqueues metabox CSS
     */
    public function test_enqueue_admin_assets_enqueues_metabox_css() {
        global $test_enqueued_styles, $post;
        $post = (object) ['ID' => 123];
        
        svp_enqueue_admin_assets('post.php');
        
        $this->assertArrayHasKey('svp-metabox', $test_enqueued_styles);
    }

    /**
     * Test enqueue admin assets enqueues metabox JS
     */
    public function test_enqueue_admin_assets_enqueues_metabox_js() {
        global $test_enqueued_scripts, $post;
        $post = (object) ['ID' => 123];
        
        svp_enqueue_admin_assets('post.php');
        
        $this->assertArrayHasKey('svp-metabox', $test_enqueued_scripts);
    }

    /**
     * Test enqueue admin assets with no post
     */
    public function test_enqueue_admin_assets_with_no_post() {
        global $test_enqueued_scripts, $test_enqueued_styles, $post;
        $post = null;
        
        svp_enqueue_admin_assets('post.php');
        
        // Should still enqueue assets even without post
        $this->assertNotEmpty($test_enqueued_styles);
        $this->assertNotEmpty($test_enqueued_scripts);
    }

    /**
     * Test add meta box function exists
     */
    public function test_add_meta_box_function_exists() {
        $this->assertTrue(function_exists('svp_add_meta_box'));
    }

    /**
     * Test schema metabox callback function exists
     */
    public function test_schema_metabox_callback_function_exists() {
        $this->assertTrue(function_exists('svp_schema_metabox_callback'));
    }

    /**
     * Test schema metabox callback outputs HTML
     */
    public function test_schema_metabox_callback_outputs_html() {
        global $post;
        $post = (object) ['ID' => 123];

        ob_start();
        svp_schema_metabox_callback($post);
        $output = ob_get_clean();

        $this->assertNotEmpty($output);
        $this->assertStringContainsString('svp-schema-metabox', $output);
    }

    /**
     * Test schema metabox callback with existing schema
     */
    public function test_schema_metabox_callback_with_existing_schema() {
        global $post, $test_post_meta;
        $post = (object) ['ID' => 123];
        
        $schema = ['@type' => 'Article', 'headline' => 'Test'];
        $test_post_meta = [123 => ['_svp_schema' => [json_encode($schema)]]];
        
        ob_start();
        svp_schema_metabox_callback($post);
        $output = ob_get_clean();
        
        $this->assertStringContainsString('Test', $output);
    }

    /**
     * Test schema metabox callback with no schema
     */
    public function test_schema_metabox_callback_with_no_schema() {
        global $post, $test_post_meta;
        $post = (object) ['ID' => 123];
        $test_post_meta = [123 => []];
        
        ob_start();
        svp_schema_metabox_callback($post);
        $output = ob_get_clean();
        
        $this->assertNotEmpty($output);
    }

    /**
     * Test schema metabox callback includes schema type selector
     */
    public function test_schema_metabox_callback_includes_schema_type_selector() {
        global $post;
        $post = (object) ['ID' => 123];
        
        ob_start();
        svp_schema_metabox_callback($post);
        $output = ob_get_clean();
        
        $this->assertStringContainsString('select', $output);
    }

    /**
     * Test schema metabox callback includes generate button
     */
    public function test_schema_metabox_callback_includes_generate_button() {
        global $post;
        $post = (object) ['ID' => 123];
        
        ob_start();
        svp_schema_metabox_callback($post);
        $output = ob_get_clean();
        
        $this->assertStringContainsString('button', $output);
    }

    /**
     * Test settings page function exists
     */
    public function test_settings_page_function_exists() {
        $this->assertTrue(function_exists('svp_settings_page'));
    }

    /**
     * Test admin page function exists
     */
    public function test_admin_page_function_exists() {
        $this->assertTrue(function_exists('svp_admin_page'));
    }

    /**
     * Test admin page outputs HTML
     */
    public function test_admin_page_outputs_html() {
        ob_start();
        svp_admin_page();
        $output = ob_get_clean();
        
        $this->assertNotEmpty($output);
        $this->assertStringContainsString('Schema Validator Pro', $output);
    }

    /**
     * Test admin page includes how it works section
     */
    public function test_admin_page_includes_how_it_works() {
        ob_start();
        svp_admin_page();
        $output = ob_get_clean();

        $this->assertStringContainsString('How It Works', $output);
    }

    /**
     * Test admin page includes supported schema types
     */
    public function test_admin_page_includes_supported_types() {
        ob_start();
        svp_admin_page();
        $output = ob_get_clean();

        $this->assertStringContainsString('Article', $output);
        $this->assertStringContainsString('Product', $output);
    }

    /**
     * Test clear cache on post update function exists
     */
    public function test_clear_cache_on_post_update_function_exists() {
        $this->assertTrue(function_exists('svp_clear_cache_on_post_update'));
    }

    /**
     * Test clear cache on post update clears cache
     */
    public function test_clear_cache_on_post_update_clears_cache() {
        global $test_transients;
        
        // Set some cached schemas
        $cache_key = svp_get_schema_cache_key(123, 'Article');
        $test_transients[$cache_key] = ['@type' => 'Article'];
        
        svp_clear_cache_on_post_update(123);
        
        // Cache should be cleared
        $result = svp_get_cached_schema(123, 'Article');
        $this->assertFalse($result);
    }

    /**
     * Test clear cache on post update with multiple schema types
     */
    public function test_clear_cache_on_post_update_clears_all_types() {
        global $test_transients;
        
        // Set multiple cached schemas
        $types = ['Article', 'Product', 'Recipe'];
        foreach ($types as $type) {
            $cache_key = svp_get_schema_cache_key(123, $type);
            $test_transients[$cache_key] = ['@type' => $type];
        }
        
        svp_clear_cache_on_post_update(123);
        
        // All caches should be cleared
        foreach ($types as $type) {
            $result = svp_get_cached_schema(123, $type);
            $this->assertFalse($result);
        }
    }
}

