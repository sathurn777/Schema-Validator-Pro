<?php
/**
 * Tests for Schema Injection Functions
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class InjectionTest extends TestCase {

    private static $plugin_loaded = false;

    public static function setUpBeforeClass(): void {
        parent::setUpBeforeClass();
        
        if (!self::$plugin_loaded) {
            require_once dirname(__DIR__) . '/schema-validator-pro.php';
            self::$plugin_loaded = true;
        }
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

    /**
     * Test svp_clear_cache_on_post_update function exists
     */
    public function test_clear_cache_on_post_update_function_exists() {
        $this->assertTrue(function_exists('svp_clear_cache_on_post_update'));
    }

    /**
     * Test svp_get_cached_schema function exists
     */
    public function test_get_cached_schema_function_exists() {
        $this->assertTrue(function_exists('svp_get_cached_schema'));
    }

    /**
     * Test svp_set_cached_schema function exists
     */
    public function test_set_cached_schema_function_exists() {
        $this->assertTrue(function_exists('svp_set_cached_schema'));
    }

    /**
     * Test svp_clear_cached_schema function exists
     */
    public function test_clear_cached_schema_function_exists() {
        $this->assertTrue(function_exists('svp_clear_cached_schema'));
    }

    /**
     * Test cache key generation with different post IDs
     */
    public function test_cache_key_generation_different_posts() {
        $key1 = svp_get_schema_cache_key(1, 'Article');
        $key2 = svp_get_schema_cache_key(2, 'Article');
        
        $this->assertNotEquals($key1, $key2);
    }

    /**
     * Test cache key generation with different schema types
     */
    public function test_cache_key_generation_different_types() {
        $key1 = svp_get_schema_cache_key(1, 'Article');
        $key2 = svp_get_schema_cache_key(1, 'Product');
        
        $this->assertNotEquals($key1, $key2);
    }

    /**
     * Test cache key format
     */
    public function test_cache_key_format() {
        $key = svp_get_schema_cache_key(123, 'Article');
        
        $this->assertEquals('svp_schema_123_Article', $key);
    }

    /**
     * Test cache key with zero post ID
     */
    public function test_cache_key_zero_post_id() {
        $key = svp_get_schema_cache_key(0, 'Article');
        
        $this->assertEquals('svp_schema_0_Article', $key);
    }

    /**
     * Test cache key with large post ID
     */
    public function test_cache_key_large_post_id() {
        $key = svp_get_schema_cache_key(999999, 'Article');
        
        $this->assertEquals('svp_schema_999999_Article', $key);
    }

    /**
     * Test cache key with all schema types
     */
    public function test_cache_key_all_schema_types() {
        $types = ['Article', 'Product', 'Recipe', 'HowTo', 'FAQPage', 'Event', 'Person', 'Organization', 'Course'];
        
        foreach ($types as $type) {
            $key = svp_get_schema_cache_key(1, $type);
            $this->assertStringContainsString($type, $key);
        }
    }

    /**
     * Test cache key uniqueness
     */
    public function test_cache_key_uniqueness() {
        $keys = [];
        for ($i = 1; $i <= 10; $i++) {
            $keys[] = svp_get_schema_cache_key($i, 'Article');
        }
        
        $unique_keys = array_unique($keys);
        $this->assertCount(10, $unique_keys);
    }
}

