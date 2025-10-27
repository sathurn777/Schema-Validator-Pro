<?php
/**
 * Simple Tests for Schema Caching Functions
 * Tests the logic without mocking WordPress functions
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class CacheSimpleTest extends TestCase {

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
     * Test svp_get_schema_cache_key() generates correct cache key
     */
    public function test_get_schema_cache_key_format() {
        $post_id = 123;
        $schema_type = 'Article';
        
        $cache_key = svp_get_schema_cache_key($post_id, $schema_type);
        
        $this->assertEquals('svp_schema_123_Article', $cache_key);
    }

    /**
     * Test svp_get_schema_cache_key() with different post IDs
     */
    public function test_get_schema_cache_key_different_post_ids() {
        $cache_key_1 = svp_get_schema_cache_key(123, 'Article');
        $cache_key_2 = svp_get_schema_cache_key(456, 'Article');
        
        $this->assertNotEquals($cache_key_1, $cache_key_2);
        $this->assertEquals('svp_schema_123_Article', $cache_key_1);
        $this->assertEquals('svp_schema_456_Article', $cache_key_2);
    }

    /**
     * Test svp_get_schema_cache_key() with different schema types
     */
    public function test_get_schema_cache_key_different_schema_types() {
        $cache_key_1 = svp_get_schema_cache_key(123, 'Article');
        $cache_key_2 = svp_get_schema_cache_key(123, 'Product');
        
        $this->assertNotEquals($cache_key_1, $cache_key_2);
        $this->assertEquals('svp_schema_123_Article', $cache_key_1);
        $this->assertEquals('svp_schema_123_Product', $cache_key_2);
    }

    /**
     * Test cache key with zero post ID
     */
    public function test_get_schema_cache_key_zero_post_id() {
        $cache_key = svp_get_schema_cache_key(0, 'Article');
        
        $this->assertEquals('svp_schema_0_Article', $cache_key);
    }

    /**
     * Test cache key with large post ID
     */
    public function test_get_schema_cache_key_large_post_id() {
        $cache_key = svp_get_schema_cache_key(999999, 'Article');
        
        $this->assertEquals('svp_schema_999999_Article', $cache_key);
    }

    /**
     * Test cache key with all supported schema types
     */
    public function test_get_schema_cache_key_all_types() {
        $types = ['Article', 'Product', 'Recipe', 'HowTo', 'FAQPage', 'Event', 'Person', 'Organization', 'Course'];
        $post_id = 123;
        
        foreach ($types as $type) {
            $cache_key = svp_get_schema_cache_key($post_id, $type);
            $this->assertEquals("svp_schema_123_{$type}", $cache_key);
        }
    }
}

