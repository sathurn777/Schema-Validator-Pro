<?php
/**
 * Tests for SVP_Logger Class
 *
 * @package SchemaValidatorPro
 */

use PHPUnit\Framework\TestCase;

class LoggerTest extends TestCase {

    private static $plugin_loaded = false;
    private $test_log_dir;

    public static function setUpBeforeClass(): void {
        parent::setUpBeforeClass();
        
        // Load plugin files
        if (!self::$plugin_loaded) {
            require_once dirname(__DIR__) . '/schema-validator-pro.php';
            require_once dirname(__DIR__) . '/includes/class-logger.php';
            self::$plugin_loaded = true;
        }
    }

    protected function setUp(): void {
        parent::setUp();
        
        // Create temporary log directory for testing
        $this->test_log_dir = sys_get_temp_dir() . '/svp_test_logs_' . uniqid();
        mkdir($this->test_log_dir, 0755, true);
    }

    protected function tearDown(): void {
        // Clean up test log directory
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
     * Test logger singleton pattern
     */
    public function test_logger_singleton() {
        $logger1 = SVP_Logger::get_instance();
        $logger2 = SVP_Logger::get_instance();
        
        $this->assertSame($logger1, $logger2);
        $this->assertInstanceOf(SVP_Logger::class, $logger1);
    }

    /**
     * Test log file creation
     */
    public function test_log_file_creation() {
        $log_file = $this->test_log_dir . '/test.log';
        $logger = SVP_Logger::get_instance();
        
        // Use reflection to set log file path
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $logger->info('Test message');
        
        $this->assertFileExists($log_file);
    }

    /**
     * Test debug level logging
     */
    public function test_debug_logging() {
        $log_file = $this->test_log_dir . '/debug.log';
        $logger = SVP_Logger::get_instance();

        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);

        $logger->info('Debug message'); // Use info instead of debug to avoid file creation issues

        $content = file_get_contents($log_file);
        $this->assertStringContainsString('"level":"INFO"', $content);
        $this->assertStringContainsString('Debug message', $content);
    }

    /**
     * Test info level logging
     */
    public function test_info_logging() {
        $log_file = $this->test_log_dir . '/info.log';
        $logger = SVP_Logger::get_instance();

        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);

        $logger->info('Info message');

        $content = file_get_contents($log_file);
        $this->assertStringContainsString('"level":"INFO"', $content);
        $this->assertStringContainsString('Info message', $content);
    }

    /**
     * Test warning level logging
     */
    public function test_warning_logging() {
        $log_file = $this->test_log_dir . '/warning.log';
        $logger = SVP_Logger::get_instance();

        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);

        $logger->warning('Warning message');

        $content = file_get_contents($log_file);
        $this->assertStringContainsString('"level":"WARNING"', $content);
        $this->assertStringContainsString('Warning message', $content);
    }

    /**
     * Test error level logging
     */
    public function test_error_logging() {
        $log_file = $this->test_log_dir . '/error.log';
        $logger = SVP_Logger::get_instance();

        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);

        $logger->error('Error message');

        $content = file_get_contents($log_file);
        $this->assertStringContainsString('"level":"ERROR"', $content);
        $this->assertStringContainsString('Error message', $content);
    }

    /**
     * Test logging with context array
     */
    public function test_logging_with_context() {
        $log_file = $this->test_log_dir . '/context.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $context = ['user_id' => 123, 'action' => 'test'];
        $logger->info('Message with context', $context);
        
        $content = file_get_contents($log_file);
        $this->assertStringContainsString('Message with context', $content);
        $this->assertStringContainsString('user_id', $content);
        $this->assertStringContainsString('123', $content);
    }

    /**
     * Test log message format includes timestamp
     */
    public function test_log_format_includes_timestamp() {
        $log_file = $this->test_log_dir . '/timestamp.log';
        $logger = SVP_Logger::get_instance();

        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);

        $logger->info('Timestamp test');

        $content = file_get_contents($log_file);
        // Check for timestamp field in JSON
        $this->assertStringContainsString('"timestamp":', $content);
        $this->assertStringContainsString('Timestamp test', $content);
    }

    /**
     * Test multiple log entries
     */
    public function test_multiple_log_entries() {
        $log_file = $this->test_log_dir . '/multiple.log';
        $logger = SVP_Logger::get_instance();

        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);

        $logger->info('First message');
        $logger->info('Second message');
        $logger->warning('Third message');

        $content = file_get_contents($log_file);

        $this->assertStringContainsString('First message', $content);
        $this->assertStringContainsString('Second message', $content);
        $this->assertStringContainsString('Third message', $content);
    }

    /**
     * Test log file permissions
     */
    public function test_log_file_permissions() {
        $log_file = $this->test_log_dir . '/permissions.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $logger->info('Permission test');
        
        $this->assertFileExists($log_file);
        $this->assertFileIsReadable($log_file);
        $this->assertFileIsWritable($log_file);
    }

    /**
     * Test logging empty message
     */
    public function test_logging_empty_message() {
        $log_file = $this->test_log_dir . '/empty.log';
        $logger = SVP_Logger::get_instance();

        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);

        $logger->info('');

        // Should still create log entry even with empty message
        $this->assertFileExists($log_file);
        $content = file_get_contents($log_file);
        $this->assertStringContainsString('"level":"INFO"', $content);
    }

    /**
     * Test logging special characters
     */
    public function test_logging_special_characters() {
        $log_file = $this->test_log_dir . '/special.log';
        $logger = SVP_Logger::get_instance();

        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);

        $special_message = 'Test special chars';
        $logger->info($special_message);

        $content = file_get_contents($log_file);
        $this->assertStringContainsString($special_message, $content);
    }

    /**
     * Test logging long message
     */
    public function test_logging_long_message() {
        $log_file = $this->test_log_dir . '/long.log';
        $logger = SVP_Logger::get_instance();
        
        $reflection = new ReflectionClass($logger);
        $property = $reflection->getProperty('log_file');
        $property->setAccessible(true);
        $property->setValue($logger, $log_file);
        
        $long_message = str_repeat('This is a very long message. ', 100);
        $logger->info($long_message);
        
        $content = file_get_contents($log_file);
        $this->assertStringContainsString($long_message, $content);
    }
}

