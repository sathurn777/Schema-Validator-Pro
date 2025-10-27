<?php
/**
 * Logger class for Schema Validator Pro
 *
 * Provides structured logging for WordPress plugin operations.
 *
 * @package Schema_Validator_Pro
 * @since 1.0.0
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

class SVP_Logger {
    /**
     * Log levels
     */
    const LEVEL_DEBUG = 'debug';
    const LEVEL_INFO = 'info';
    const LEVEL_WARNING = 'warning';
    const LEVEL_ERROR = 'error';
    
    /**
     * Log file path
     *
     * @var string
     */
    private $log_file;
    
    /**
     * Maximum log file size (10MB)
     *
     * @var int
     */
    private $max_file_size = 10485760;
    
    /**
     * Current log level
     *
     * @var string
     */
    private $log_level;
    
    /**
     * Singleton instance
     *
     * @var SVP_Logger
     */
    private static $instance = null;
    
    /**
     * Get singleton instance
     *
     * @return SVP_Logger
     */
    public static function get_instance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    /**
     * Constructor
     */
    private function __construct() {
        $upload_dir = wp_upload_dir();
        $log_dir = $upload_dir['basedir'] . '/schema-validator-pro-logs';
        
        // Create log directory if it doesn't exist
        if (!file_exists($log_dir)) {
            wp_mkdir_p($log_dir);
            
            // Add .htaccess to protect logs
            $htaccess = $log_dir . '/.htaccess';
            if (!file_exists($htaccess)) {
                file_put_contents($htaccess, "Deny from all\n");
            }
        }
        
        $this->log_file = $log_dir . '/schema-validator-pro.log';
        $this->log_level = get_option('svp_log_level', self::LEVEL_INFO);
    }
    
    /**
     * Log a message
     *
     * @param string $level Log level
     * @param string $message Log message
     * @param array $context Additional context
     */
    public function log($level, $message, $context = array()) {
        // Check if we should log this level
        if (!$this->should_log($level)) {
            return;
        }
        
        // Rotate log if needed
        $this->rotate_log_if_needed();
        
        // Format log entry
        $entry = $this->format_log_entry($level, $message, $context);
        
        // Write to file
        error_log($entry . "\n", 3, $this->log_file);
        
        // Also log errors to WordPress debug log if WP_DEBUG is enabled
        if ($level === self::LEVEL_ERROR && defined('WP_DEBUG') && WP_DEBUG) {
            error_log('[Schema Validator Pro] ' . $message);
        }
    }
    
    /**
     * Log debug message
     *
     * @param string $message Log message
     * @param array $context Additional context
     */
    public function debug($message, $context = array()) {
        $this->log(self::LEVEL_DEBUG, $message, $context);
    }
    
    /**
     * Log info message
     *
     * @param string $message Log message
     * @param array $context Additional context
     */
    public function info($message, $context = array()) {
        $this->log(self::LEVEL_INFO, $message, $context);
    }
    
    /**
     * Log warning message
     *
     * @param string $message Log message
     * @param array $context Additional context
     */
    public function warning($message, $context = array()) {
        $this->log(self::LEVEL_WARNING, $message, $context);
    }
    
    /**
     * Log error message
     *
     * @param string $message Log message
     * @param array $context Additional context
     */
    public function error($message, $context = array()) {
        $this->log(self::LEVEL_ERROR, $message, $context);
    }
    
    /**
     * Check if we should log this level
     *
     * @param string $level Log level to check
     * @return bool
     */
    private function should_log($level) {
        $levels = array(
            self::LEVEL_DEBUG => 0,
            self::LEVEL_INFO => 1,
            self::LEVEL_WARNING => 2,
            self::LEVEL_ERROR => 3,
        );
        
        $current_level = isset($levels[$this->log_level]) ? $levels[$this->log_level] : 1;
        $message_level = isset($levels[$level]) ? $levels[$level] : 1;
        
        return $message_level >= $current_level;
    }
    
    /**
     * Format log entry
     *
     * @param string $level Log level
     * @param string $message Log message
     * @param array $context Additional context
     * @return string
     */
    private function format_log_entry($level, $message, $context) {
        $timestamp = current_time('Y-m-d H:i:s');
        $user_id = get_current_user_id();
        
        $entry = array(
            'timestamp' => $timestamp,
            'level' => strtoupper($level),
            'message' => $message,
            'user_id' => $user_id,
        );
        
        if (!empty($context)) {
            $entry['context'] = $context;
        }
        
        return wp_json_encode($entry, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    }
    
    /**
     * Rotate log file if it exceeds max size
     */
    private function rotate_log_if_needed() {
        if (!file_exists($this->log_file)) {
            return;
        }
        
        $file_size = filesize($this->log_file);
        if ($file_size < $this->max_file_size) {
            return;
        }
        
        // Rotate: rename current log to .1, .1 to .2, etc.
        for ($i = 4; $i >= 1; $i--) {
            $old_file = $this->log_file . '.' . $i;
            $new_file = $this->log_file . '.' . ($i + 1);
            
            if (file_exists($old_file)) {
                if ($i === 4) {
                    // Delete oldest log
                    unlink($old_file);
                } else {
                    rename($old_file, $new_file);
                }
            }
        }
        
        // Rename current log to .1
        rename($this->log_file, $this->log_file . '.1');
    }
    
    /**
     * Get recent log entries
     *
     * @param int $limit Number of entries to retrieve
     * @return array
     */
    public function get_recent_logs($limit = 100) {
        if (!file_exists($this->log_file)) {
            return array();
        }
        
        $lines = file($this->log_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        if ($lines === false) {
            return array();
        }
        
        // Get last N lines
        $lines = array_slice($lines, -$limit);
        
        // Parse JSON entries
        $logs = array();
        foreach (array_reverse($lines) as $line) {
            $entry = json_decode($line, true);
            if ($entry !== null) {
                $logs[] = $entry;
            }
        }
        
        return $logs;
    }
    
    /**
     * Clear all logs
     */
    public function clear_logs() {
        if (file_exists($this->log_file)) {
            unlink($this->log_file);
        }
        
        // Also delete rotated logs
        for ($i = 1; $i <= 5; $i++) {
            $rotated_file = $this->log_file . '.' . $i;
            if (file_exists($rotated_file)) {
                unlink($rotated_file);
            }
        }
    }
    
    /**
     * Get log file size
     *
     * @return int Size in bytes
     */
    public function get_log_size() {
        if (!file_exists($this->log_file)) {
            return 0;
        }
        return filesize($this->log_file);
    }
    
    /**
     * Get log file path
     *
     * @return string
     */
    public function get_log_file_path() {
        return $this->log_file;
    }
}

/**
 * Get logger instance
 *
 * @return SVP_Logger
 */
function svp_logger() {
    return SVP_Logger::get_instance();
}

