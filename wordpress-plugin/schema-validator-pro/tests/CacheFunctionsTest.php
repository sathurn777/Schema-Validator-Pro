<?php
/**
 * Tests for Cache Functions
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class CacheFunctionsTest extends TestCase {

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

        // Clear all transients before each test
        global $test_transients;
        $test_transients = [];
    }

    protected function tearDown(): void {
        // Clear all transients after each test
        global $test_transients;
        $test_transients = [];

        parent::tearDown();
    }

    /**
     * Test get cached schema returns false when not cached
     */
    public function test_get_cached_schema_returns_false_when_not_cached() {
        $result = svp_get_cached_schema(123, 'Article');
        
        $this->assertFalse($result);
    }

    /**
     * Test set and get cached schema
     */
    public function test_set_and_get_cached_schema() {
        $schema = [
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => 'Test Article',
        ];
        
        // Set cache
        svp_set_cached_schema(123, 'Article', $schema, 3600);
        
        // Get cache
        $cached = svp_get_cached_schema(123, 'Article');
        
        $this->assertIsArray($cached);
        $this->assertEquals('Article', $cached['@type']);
        $this->assertEquals('Test Article', $cached['headline']);
    }

    /**
     * Test set cached schema with different post IDs
     */
    public function test_set_cached_schema_different_post_ids() {
        $schema1 = ['@type' => 'Article', 'headline' => 'Article 1'];
        $schema2 = ['@type' => 'Article', 'headline' => 'Article 2'];
        
        svp_set_cached_schema(1, 'Article', $schema1, 3600);
        svp_set_cached_schema(2, 'Article', $schema2, 3600);
        
        $cached1 = svp_get_cached_schema(1, 'Article');
        $cached2 = svp_get_cached_schema(2, 'Article');
        
        $this->assertEquals('Article 1', $cached1['headline']);
        $this->assertEquals('Article 2', $cached2['headline']);
    }

    /**
     * Test set cached schema with different schema types
     */
    public function test_set_cached_schema_different_types() {
        $article = ['@type' => 'Article', 'headline' => 'Test'];
        $product = ['@type' => 'Product', 'name' => 'Test Product'];
        
        svp_set_cached_schema(1, 'Article', $article, 3600);
        svp_set_cached_schema(1, 'Product', $product, 3600);
        
        $cached_article = svp_get_cached_schema(1, 'Article');
        $cached_product = svp_get_cached_schema(1, 'Product');
        
        $this->assertEquals('Article', $cached_article['@type']);
        $this->assertEquals('Product', $cached_product['@type']);
    }

    /**
     * Test clear cached schema
     */
    public function test_clear_cached_schema() {
        $schema = ['@type' => 'Article'];
        
        // Set cache
        svp_set_cached_schema(123, 'Article', $schema, 3600);
        
        // Verify it's cached
        $cached = svp_get_cached_schema(123, 'Article');
        $this->assertIsArray($cached);
        
        // Clear cache
        svp_clear_cached_schema(123, 'Article');
        
        // Verify it's cleared
        $cached = svp_get_cached_schema(123, 'Article');
        $this->assertFalse($cached);
    }

    /**
     * Test clear cached schema for specific type only
     */
    public function test_clear_cached_schema_specific_type() {
        $article = ['@type' => 'Article'];
        $product = ['@type' => 'Product'];
        
        svp_set_cached_schema(1, 'Article', $article, 3600);
        svp_set_cached_schema(1, 'Product', $product, 3600);
        
        // Clear only Article
        svp_clear_cached_schema(1, 'Article');
        
        // Article should be cleared
        $this->assertFalse(svp_get_cached_schema(1, 'Article'));
        
        // Product should still be cached
        $this->assertIsArray(svp_get_cached_schema(1, 'Product'));
    }

    /**
     * Test clear cache on post update
     */
    public function test_clear_cache_on_post_update() {
        // Set multiple caches for same post
        svp_set_cached_schema(456, 'Article', ['@type' => 'Article'], 3600);
        svp_set_cached_schema(456, 'Product', ['@type' => 'Product'], 3600);
        
        // Clear all caches for post
        svp_clear_cache_on_post_update(456);
        
        // Both should be cleared
        $this->assertFalse(svp_get_cached_schema(456, 'Article'));
        $this->assertFalse(svp_get_cached_schema(456, 'Product'));
    }

    /**
     * Test cache key format
     */
    public function test_cache_key_format() {
        $key = svp_get_schema_cache_key(123, 'Article');
        
        $this->assertEquals('svp_schema_123_Article', $key);
    }

    /**
     * Test cache with empty schema
     */
    public function test_cache_with_empty_schema() {
        $schema = [];
        
        svp_set_cached_schema(789, 'Article', $schema, 3600);
        
        $cached = svp_get_cached_schema(789, 'Article');
        
        $this->assertIsArray($cached);
        $this->assertEmpty($cached);
    }

    /**
     * Test cache with complex schema
     */
    public function test_cache_with_complex_schema() {
        $schema = [
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => 'Test',
            'author' => [
                '@type' => 'Person',
                'name' => 'John Doe',
            ],
            'publisher' => [
                '@type' => 'Organization',
                'name' => 'Test Org',
                'logo' => [
                    '@type' => 'ImageObject',
                    'url' => 'https://example.com/logo.png',
                ],
            ],
        ];
        
        svp_set_cached_schema(999, 'Article', $schema, 3600);
        
        $cached = svp_get_cached_schema(999, 'Article');
        
        $this->assertIsArray($cached);
        $this->assertEquals('John Doe', $cached['author']['name']);
        $this->assertEquals('Test Org', $cached['publisher']['name']);
    }

    /**
     * Test cache with special characters
     */
    public function test_cache_with_special_characters() {
        $schema = [
            '@type' => 'Article',
            'headline' => 'Test "quotes" & <html> \' special',
        ];
        
        svp_set_cached_schema(111, 'Article', $schema, 3600);
        
        $cached = svp_get_cached_schema(111, 'Article');
        
        $this->assertEquals('Test "quotes" & <html> \' special', $cached['headline']);
    }

    /**
     * Test cache with unicode characters
     */
    public function test_cache_with_unicode() {
        $schema = [
            '@type' => 'Article',
            'headline' => '测试中文 🎉 Émojis',
        ];
        
        svp_set_cached_schema(222, 'Article', $schema, 3600);
        
        $cached = svp_get_cached_schema(222, 'Article');
        
        $this->assertEquals('测试中文 🎉 Émojis', $cached['headline']);
    }

    /**
     * Test cache expiration time
     */
    public function test_cache_expiration_time() {
        $schema = ['@type' => 'Article'];
        
        // Set cache with 1 hour expiration
        svp_set_cached_schema(333, 'Article', $schema, 3600);
        
        // Should be cached
        $this->assertIsArray(svp_get_cached_schema(333, 'Article'));
    }

    /**
     * Test cache with zero post ID
     */
    public function test_cache_with_zero_post_id() {
        $schema = ['@type' => 'Article'];
        
        svp_set_cached_schema(0, 'Article', $schema, 3600);
        
        $cached = svp_get_cached_schema(0, 'Article');
        
        $this->assertIsArray($cached);
    }

    /**
     * Test cache with negative post ID
     */
    public function test_cache_with_negative_post_id() {
        $schema = ['@type' => 'Article'];
        
        svp_set_cached_schema(-1, 'Article', $schema, 3600);
        
        $cached = svp_get_cached_schema(-1, 'Article');
        
        $this->assertIsArray($cached);
    }

    /**
     * Test cache with very large post ID
     */
    public function test_cache_with_large_post_id() {
        $schema = ['@type' => 'Article'];
        
        svp_set_cached_schema(999999999, 'Article', $schema, 3600);
        
        $cached = svp_get_cached_schema(999999999, 'Article');
        
        $this->assertIsArray($cached);
    }
}

