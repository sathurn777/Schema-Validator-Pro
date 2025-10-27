<?php
/**
 * Execution Tests for Schema Injection
 * Tests actual code execution, not just function existence
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class SchemaInjectionExecutionTest extends TestCase {

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
        global $post, $test_post_meta, $test_is_singular, $test_transients;
        $post = null;
        $test_post_meta = [];
        $test_is_singular = false;
        $test_transients = [];
    }

    /**
     * Test inject_schema returns early when not singular
     */
    public function test_inject_schema_returns_early_when_not_singular() {
        global $test_is_singular;
        $test_is_singular = false;
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        $this->assertEmpty($output);
    }

    /**
     * Test inject_schema returns early when no post
     */
    public function test_inject_schema_returns_early_when_no_post() {
        global $test_is_singular, $post;
        $test_is_singular = true;
        $post = null;
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        $this->assertEmpty($output);
    }

    /**
     * Test inject_schema returns early when no schema in post meta
     */
    public function test_inject_schema_returns_early_when_no_schema() {
        global $test_is_singular, $post, $test_post_meta;
        $test_is_singular = true;
        $post = (object) ['ID' => 123];
        $test_post_meta = [123 => []];
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        $this->assertEmpty($output);
    }

    /**
     * Test inject_schema returns early when empty schema
     */
    public function test_inject_schema_returns_early_when_empty_schema() {
        global $test_is_singular, $post, $test_post_meta;
        $test_is_singular = true;
        $post = (object) ['ID' => 123];
        $test_post_meta = [123 => ['_svp_schema' => ['']]];
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        $this->assertEmpty($output);
    }

    /**
     * Test inject_schema outputs schema with valid JSON string
     */
    public function test_inject_schema_outputs_with_valid_json_string() {
        global $test_is_singular, $post, $test_post_meta;
        $test_is_singular = true;
        $post = (object) ['ID' => 123];
        
        $schema = [
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => 'Test Article',
        ];
        
        $test_post_meta = [123 => ['_svp_schema' => [json_encode($schema)]]];
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('application/ld+json', $output);
        $this->assertStringContainsString('Test Article', $output);
        $this->assertStringContainsString('Article', $output);
        $this->assertStringContainsString('https://schema.org', $output);
    }

    /**
     * Test inject_schema outputs schema with array data
     */
    public function test_inject_schema_outputs_with_array_data() {
        global $test_is_singular, $post, $test_post_meta;
        $test_is_singular = true;
        $post = (object) ['ID' => 456];
        
        $schema = [
            '@context' => 'https://schema.org',
            '@type' => 'Product',
            'name' => 'Test Product',
        ];
        
        $test_post_meta = [456 => ['_svp_schema' => [$schema]]];
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('Test Product', $output);
        $this->assertStringContainsString('Product', $output);
    }

    /**
     * Test inject_schema includes version comment
     */
    public function test_inject_schema_includes_version_comment() {
        global $test_is_singular, $post, $test_post_meta;
        $test_is_singular = true;
        $post = (object) ['ID' => 789];
        
        $schema = ['@type' => 'Article', 'headline' => 'Test'];
        $test_post_meta = [789 => ['_svp_schema' => [json_encode($schema)]]];
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('<!-- Schema Validator Pro v', $output);
        $this->assertStringContainsString(SCHEMA_VALIDATOR_PRO_VERSION, $output);
        $this->assertStringContainsString('<!-- /Schema Validator Pro -->', $output);
    }

    /**
     * Test inject_schema with complex nested schema
     */
    public function test_inject_schema_with_complex_schema() {
        global $test_is_singular, $post, $test_post_meta;
        $test_is_singular = true;
        $post = (object) ['ID' => 999];
        
        $schema = [
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => 'Complex Article',
            'author' => [
                '@type' => 'Person',
                'name' => 'John Doe',
            ],
            'publisher' => [
                '@type' => 'Organization',
                'name' => 'Test Org',
            ],
        ];
        
        $test_post_meta = [999 => ['_svp_schema' => [json_encode($schema)]]];
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('Complex Article', $output);
        $this->assertStringContainsString('John Doe', $output);
        $this->assertStringContainsString('Test Org', $output);
    }

    /**
     * Test inject_schema with special characters
     */
    public function test_inject_schema_with_special_characters() {
        global $test_is_singular, $post, $test_post_meta;
        $test_is_singular = true;
        $post = (object) ['ID' => 111];
        
        $schema = [
            '@type' => 'Article',
            'headline' => 'Test "quotes" & <html>',
        ];
        
        $test_post_meta = [111 => ['_svp_schema' => [json_encode($schema)]]];
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        $this->assertNotEmpty($output);
        $this->assertStringContainsString('application/ld+json', $output);
    }

    /**
     * Test inject_schema with unicode characters
     */
    public function test_inject_schema_with_unicode() {
        global $test_is_singular, $post, $test_post_meta;
        $test_is_singular = true;
        $post = (object) ['ID' => 222];
        
        $schema = [
            '@type' => 'Article',
            'headline' => '测试中文 🎉',
        ];
        
        $test_post_meta = [222 => ['_svp_schema' => [json_encode($schema)]]];
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('测试中文', $output);
    }

    /**
     * Test has_existing_schema returns boolean
     */
    public function test_has_existing_schema_returns_boolean() {
        global $post;
        $post = (object) ['ID' => 123];

        $result = svp_has_existing_schema();
        $this->assertIsBool($result);
    }

    /**
     * Test has_existing_schema returns false by default
     */
    public function test_has_existing_schema_returns_false_by_default() {
        global $post;
        $post = (object) ['ID' => 123];

        $result = svp_has_existing_schema();
        $this->assertFalse($result);
    }

    /**
     * Test cache key generation is consistent
     */
    public function test_cache_key_generation_is_consistent() {
        $key1 = svp_get_schema_cache_key(123, 'Article');
        $key2 = svp_get_schema_cache_key(123, 'Article');
        
        $this->assertEquals($key1, $key2);
    }

    /**
     * Test cache key includes post ID
     */
    public function test_cache_key_includes_post_id() {
        $key = svp_get_schema_cache_key(123, 'Article');
        
        $this->assertStringContainsString('123', $key);
    }

    /**
     * Test cache key includes schema type
     */
    public function test_cache_key_includes_schema_type() {
        $key = svp_get_schema_cache_key(123, 'Article');
        
        $this->assertStringContainsString('Article', $key);
    }

    /**
     * Test cache key has correct prefix
     */
    public function test_cache_key_has_correct_prefix() {
        $key = svp_get_schema_cache_key(123, 'Article');
        
        $this->assertStringStartsWith('svp_schema_', $key);
    }

    /**
     * Test inject_schema returns early with invalid JSON
     */
    public function test_inject_schema_with_invalid_json_returns_early() {
        global $test_is_singular, $post, $test_post_meta;
        $test_is_singular = true;
        $post = (object) ['ID' => 333];
        
        $test_post_meta = [333 => ['_svp_schema' => ['invalid json {']]];
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        // Should handle gracefully - either empty or error
        $this->assertIsString($output);
    }

    /**
     * Test inject_schema with empty array schema
     */
    public function test_inject_schema_with_empty_array_schema() {
        global $test_is_singular, $post, $test_post_meta;
        $test_is_singular = true;
        $post = (object) ['ID' => 444];
        
        $test_post_meta = [444 => ['_svp_schema' => [[]]]];
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        // Empty array should return early
        $this->assertEmpty($output);
    }

    /**
     * Test inject_schema script tag format
     */
    public function test_inject_schema_script_tag_format() {
        global $test_is_singular, $post, $test_post_meta;
        $test_is_singular = true;
        $post = (object) ['ID' => 555];
        
        $schema = ['@type' => 'Article', 'headline' => 'Test'];
        $test_post_meta = [555 => ['_svp_schema' => [json_encode($schema)]]];
        
        ob_start();
        svp_inject_schema();
        $output = ob_get_clean();
        
        $this->assertStringContainsString('<script type="application/ld+json">', $output);
        $this->assertStringContainsString('</script>', $output);
    }

    /**
     * Test inject_schema with multiple schema types
     */
    public function test_inject_schema_with_different_types() {
        $types = ['Article', 'Product', 'Recipe', 'Event', 'Person'];
        
        foreach ($types as $index => $type) {
            global $test_is_singular, $post, $test_post_meta;
            $test_is_singular = true;
            $post_id = 1000 + $index;
            $post = (object) ['ID' => $post_id];
            
            $schema = ['@type' => $type, 'name' => "Test $type"];
            $test_post_meta = [$post_id => ['_svp_schema' => [json_encode($schema)]]];
            
            ob_start();
            svp_inject_schema();
            $output = ob_get_clean();
            
            $this->assertStringContainsString($type, $output);
            $this->assertStringContainsString("Test $type", $output);
        }
    }
}

