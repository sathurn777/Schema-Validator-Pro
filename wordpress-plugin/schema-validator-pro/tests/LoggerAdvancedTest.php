<?php
/**
 * Advanced Tests for SVP_Logger Class
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class LoggerAdvancedTest extends TestCase {

    private static $plugin_loaded = false;
    private $test_log_dir;

    public static function setUpBeforeClass(): void {
        parent::setUpBeforeClass();
        
        if (!self::$plugin_loaded) {
            require_once dirname(__DIR__) . '/schema-validator-pro.php';
            require_once dirname(__DIR__) . '/includes/class-logger.php';
            self::$plugin_loaded = true;
        }
    }

    protected function setUp(): void {
        parent::setUp();
        
        $this->test_log_dir = sys_get_temp_dir() . '/svp_test_logs_' . uniqid();
        mkdir($this->test_log_dir, 0755, true);
    }

    protected function tearDown(): void {
        if (is_dir($this->test_log_dir)) {
            $files = glob($this->test_log_dir . '/*');
            foreach ($files as $file) {
                if (is_file($file)) {
                    unlink($file);
                }
            }
            rmdir($this->test_log_dir);
        }
        
        parent::tearDown();
    }

    /**
     * Test logger with very long message
     */
    public function test_logger_very_long_message() {
        $log_file = $this->test_log_dir . '/long.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $long_message = str_repeat('This is a very long message. ', 1000);
        $logger->info($long_message);
        
        $this->assertFileExists($log_file);
        $content = file_get_contents($log_file);
        $this->assertStringContainsString('"level":"INFO"', $content);
    }

    /**
     * Test logger with array context
     */
    public function test_logger_with_array_context() {
        $log_file = $this->test_log_dir . '/context.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $context = [
            'user_id' => 123,
            'action' => 'test',
            'data' => ['key' => 'value'],
        ];
        
        $logger->info('Test message', $context);
        
        $content = file_get_contents($log_file);
        $this->assertStringContainsString('user_id', $content);
        $this->assertStringContainsString('123', $content);
    }

    /**
     * Test logger with nested context
     */
    public function test_logger_with_nested_context() {
        $log_file = $this->test_log_dir . '/nested.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $context = [
            'level1' => [
                'level2' => [
                    'level3' => 'deep value',
                ],
            ],
        ];
        
        $logger->info('Nested context', $context);
        
        $this->assertFileExists($log_file);
        $content = file_get_contents($log_file);
        $this->assertStringContainsString('level1', $content);
    }

    /**
     * Test logger JSON format
     */
    public function test_logger_json_format() {
        $log_file = $this->test_log_dir . '/json.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $logger->info('JSON test');
        
        $content = file_get_contents($log_file);
        $decoded = json_decode(trim($content), true);
        
        $this->assertIsArray($decoded);
        $this->assertArrayHasKey('timestamp', $decoded);
        $this->assertArrayHasKey('level', $decoded);
        $this->assertArrayHasKey('message', $decoded);
    }

    /**
     * Test logger timestamp format
     */
    public function test_logger_timestamp_format() {
        $log_file = $this->test_log_dir . '/timestamp.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $logger->info('Timestamp test');
        
        $content = file_get_contents($log_file);
        $decoded = json_decode(trim($content), true);
        
        $this->assertArrayHasKey('timestamp', $decoded);
        $this->assertIsInt($decoded['timestamp']);
        $this->assertGreaterThan(0, $decoded['timestamp']);
    }

    /**
     * Test logger user_id in context
     */
    public function test_logger_user_id_in_context() {
        $log_file = $this->test_log_dir . '/user.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $logger->info('User test');
        
        $content = file_get_contents($log_file);
        $decoded = json_decode(trim($content), true);
        
        $this->assertArrayHasKey('user_id', $decoded);
    }

    /**
     * Test logger with unicode in message
     */
    public function test_logger_unicode_message() {
        $log_file = $this->test_log_dir . '/unicode.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $logger->info('测试中文 🎉 Émojis');
        
        $content = file_get_contents($log_file);
        $this->assertStringContainsString('测试中文', $content);
    }

    /**
     * Test logger with null message
     */
    public function test_logger_null_message() {
        $log_file = $this->test_log_dir . '/null.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $logger->info(null);
        
        $this->assertFileExists($log_file);
    }

    /**
     * Test logger with numeric message
     */
    public function test_logger_numeric_message() {
        $log_file = $this->test_log_dir . '/numeric.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $logger->info(12345);
        
        $content = file_get_contents($log_file);
        $this->assertStringContainsString('12345', $content);
    }

    /**
     * Test logger with boolean message
     */
    public function test_logger_boolean_message() {
        $log_file = $this->test_log_dir . '/boolean.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $logger->info(true);
        
        $this->assertFileExists($log_file);
    }

    /**
     * Test logger consecutive calls
     */
    public function test_logger_consecutive_calls() {
        $log_file = $this->test_log_dir . '/consecutive.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        for ($i = 0; $i < 10; $i++) {
            $logger->info("Message $i");
        }
        
        $content = file_get_contents($log_file);
        $lines = explode("\n", trim($content));
        
        $this->assertGreaterThanOrEqual(10, count($lines));
    }

    /**
     * Test logger with empty context
     */
    public function test_logger_empty_context() {
        $log_file = $this->test_log_dir . '/empty_context.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $logger->info('Test', []);
        
        $this->assertFileExists($log_file);
    }

    /**
     * Test logger level values
     */
    public function test_logger_level_values() {
        $log_file = $this->test_log_dir . '/levels.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $logger->info('Info level');
        $logger->warning('Warning level');
        $logger->error('Error level');
        
        $content = file_get_contents($log_file);
        
        $this->assertStringContainsString('"level":"INFO"', $content);
        $this->assertStringContainsString('"level":"WARNING"', $content);
        $this->assertStringContainsString('"level":"ERROR"', $content);
    }

    /**
     * Test logger file append mode
     */
    public function test_logger_file_append_mode() {
        $log_file = $this->test_log_dir . '/append.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $logger->info('First message');
        $logger->info('Second message');
        
        $content = file_get_contents($log_file);
        
        $this->assertStringContainsString('First message', $content);
        $this->assertStringContainsString('Second message', $content);
    }

    /**
     * Test svp_logger helper function
     */
    public function test_svp_logger_helper_function() {
        $logger = svp_logger();
        
        $this->assertInstanceOf(SVP_Logger::class, $logger);
    }

    /**
     * Test svp_logger returns same instance
     */
    public function test_svp_logger_returns_same_instance() {
        $logger1 = svp_logger();
        $logger2 = svp_logger();
        
        $this->assertSame($logger1, $logger2);
    }
}

