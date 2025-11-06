# WordPress 插件长期重构计划

**项目**: Schema Validator Pro - WordPress Plugin  
**当前版本**: v1.0.0  
**目标版本**: v2.0.0  
**时间跨度**: 1-2 个月

---

## 📊 问题优先级矩阵

| 问题 | 影响 | 紧急度 | 修复成本 | 优先级 | 版本 |
|------|------|--------|----------|--------|------|
| P0.1: SQL 注入风险 | 高 | 高 | 低 | P0 | v1.0.1 |
| P1.1: 主文件过长 | 高 | 中 | 高 | P1 | v2.0.0 |
| P1.2: 缺少 uninstall.php | 中 | 高 | 低 | P1 | v1.0.1 |
| P1.3: AJAX 函数复杂 | 高 | 中 | 中 | P1 | v2.0.0 |
| P2.1: 缺少速率限制 | 中 | 中 | 中 | P2 | v1.1.0 |
| P2.2: 日志文件安全 | 中 | 中 | 低 | P2 | v1.0.1 |
| P2.3: 缓存清理性能 | 低 | 中 | 低 | P2 | v1.0.1 |
| P2.4: Logger 测试不足 | 低 | 低 | 中 | P2 | v1.1.0 |
| P3.1: 魔法数字 | 低 | 低 | 低 | P3 | v1.1.0 |
| P3.2: 对象缓存支持 | 中 | 低 | 中 | P3 | v2.0.0 |

---

## 🗺️ 版本路线图

### v1.0.1 - 安全补丁（本周）

**目标**: 修复安全漏洞和关键问题  
**时间**: 1 周  
**工作量**: 2.5 小时

**包含修复**:
- ✅ P0.1: SQL 注入风险
- ✅ P1.2: 添加 uninstall.php
- ✅ P2.2: 日志文件安全
- ✅ P2.3: 缓存清理性能

### v1.1.0 - 功能增强（2 周后）

**目标**: 添加新功能和改进  
**时间**: 2 周  
**工作量**: 8-10 小时

**包含修复**:
- ✅ P2.1: API 速率限制
- ✅ P2.4: Logger 测试补充
- ✅ P3.1: 清理魔法数字
- 🆕 新功能: Schema 预览
- 🆕 新功能: 批量生成

### v2.0.0 - 架构重构（1-2 个月后）

**目标**: 重构代码架构，提升可维护性  
**时间**: 1-2 个月  
**工作量**: 20-30 小时

**包含修复**:
- ✅ P1.1: 拆分主文件（OOP 重构）
- ✅ P1.3: 简化 AJAX 函数
- ✅ P3.2: 对象缓存支持
- 🆕 新功能: REST API 支持
- 🆕 新功能: Gutenberg 块

---

## 🏗️ v2.0.0 架构重构详细计划

### 目标架构

```
schema-validator-pro/
├── schema-validator-pro.php (主入口，<100 行)
├── uninstall.php
├── includes/
│   ├── class-plugin.php (插件主类)
│   ├── class-schema-injector.php (Schema 注入)
│   ├── class-admin-ui.php (管理界面)
│   ├── class-meta-box.php (Meta Box)
│   ├── class-ajax-handler.php (AJAX 处理)
│   ├── class-cache-manager.php (缓存管理)
│   ├── class-api-client.php (API 客户端)
│   ├── class-logger.php (日志系统 ✓)
│   ├── class-rate-limiter.php (速率限制)
│   └── class-settings.php (设置管理)
├── admin/
│   ├── class-admin-page.php
│   ├── class-settings-page.php
│   └── views/
│       ├── admin-page.php
│       └── settings-page.php
├── assets/
│   ├── admin/
│   │   ├── css/
│   │   └── js/
│   └── public/
│       ├── css/
│       └── js/
├── languages/
├── tests/
└── vendor/
```

### 重构步骤

#### 阶段 1: 创建核心类（第 1-2 周）

**1.1 创建插件主类** (`includes/class-plugin.php`)

```php
<?php
/**
 * Main Plugin Class
 *
 * @package Schema_Validator_Pro
 * @since 2.0.0
 */

namespace SchemaValidatorPro;

if (!defined('ABSPATH')) {
    exit;
}

class Plugin {
    /**
     * Plugin version
     */
    const VERSION = '2.0.0';
    
    /**
     * Singleton instance
     */
    private static $instance = null;
    
    /**
     * Components
     */
    private $schema_injector;
    private $admin_ui;
    private $ajax_handler;
    private $cache_manager;
    private $api_client;
    private $logger;
    
    /**
     * Get singleton instance
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
        $this->define_constants();
        $this->load_dependencies();
        $this->init_components();
        $this->register_hooks();
    }
    
    /**
     * Define plugin constants
     */
    private function define_constants() {
        define('SVP_VERSION', self::VERSION);
        define('SVP_FILE', dirname(__DIR__) . '/schema-validator-pro.php');
        define('SVP_DIR', plugin_dir_path(SVP_FILE));
        define('SVP_URL', plugin_dir_url(SVP_FILE));
    }
    
    /**
     * Load dependencies
     */
    private function load_dependencies() {
        require_once SVP_DIR . 'includes/class-logger.php';
        require_once SVP_DIR . 'includes/class-cache-manager.php';
        require_once SVP_DIR . 'includes/class-api-client.php';
        require_once SVP_DIR . 'includes/class-schema-injector.php';
        require_once SVP_DIR . 'includes/class-ajax-handler.php';
        
        if (is_admin()) {
            require_once SVP_DIR . 'includes/class-admin-ui.php';
        }
    }
    
    /**
     * Initialize components
     */
    private function init_components() {
        $this->logger = Logger::get_instance();
        $this->cache_manager = new Cache_Manager($this->logger);
        $this->api_client = new API_Client($this->logger);
        $this->schema_injector = new Schema_Injector($this->cache_manager, $this->logger);
        $this->ajax_handler = new AJAX_Handler($this->api_client, $this->cache_manager, $this->logger);
        
        if (is_admin()) {
            $this->admin_ui = new Admin_UI($this->logger);
        }
    }
    
    /**
     * Register hooks
     */
    private function register_hooks() {
        add_action('plugins_loaded', [$this, 'load_textdomain']);
        add_action('init', [$this, 'init']);
    }
    
    /**
     * Load plugin textdomain
     */
    public function load_textdomain() {
        load_plugin_textdomain(
            'schema-validator-pro',
            false,
            dirname(plugin_basename(SVP_FILE)) . '/languages'
        );
    }
    
    /**
     * Initialize plugin
     */
    public function init() {
        $this->schema_injector->init();
        $this->ajax_handler->init();
        
        if (is_admin()) {
            $this->admin_ui->init();
        }
        
        do_action('svp_init', $this);
    }
    
    /**
     * Get component
     */
    public function get_component($name) {
        if (property_exists($this, $name)) {
            return $this->$name;
        }
        return null;
    }
}
```

**1.2 创建 Schema 注入类** (`includes/class-schema-injector.php`)

```php
<?php
/**
 * Schema Injector Class
 *
 * @package Schema_Validator_Pro
 * @since 2.0.0
 */

namespace SchemaValidatorPro;

class Schema_Injector {
    private $cache_manager;
    private $logger;
    
    public function __construct($cache_manager, $logger) {
        $this->cache_manager = $cache_manager;
        $this->logger = $logger;
    }
    
    public function init() {
        add_action('wp_head', [$this, 'inject_schema']);
    }
    
    public function inject_schema() {
        if (!is_singular()) {
            return;
        }
        
        global $post;
        if (!$post) {
            return;
        }
        
        $schema = $this->get_schema($post->ID);
        if (empty($schema)) {
            return;
        }
        
        if ($this->has_existing_schema()) {
            return;
        }
        
        $this->output_schema($schema, $post->ID);
    }
    
    private function get_schema($post_id) {
        $schema = get_post_meta($post_id, '_svp_schema', true);
        
        if (empty($schema)) {
            return null;
        }
        
        if (is_string($schema)) {
            $schema = json_decode($schema, true);
        }
        
        return apply_filters('svp_schema_data', $schema, $post_id);
    }
    
    private function has_existing_schema() {
        global $post;
        return apply_filters('svp_has_existing_schema', false, $post->ID);
    }
    
    private function output_schema($schema, $post_id) {
        do_action('svp_before_schema_injection', $schema, $post_id);
        
        echo "\n<!-- Schema Validator Pro v" . esc_attr(SVP_VERSION) . " -->\n";
        echo '<script type="application/ld+json">';
        echo wp_json_encode($schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        echo '</script>';
        echo "\n<!-- /Schema Validator Pro -->\n";
        
        do_action('svp_after_schema_injection', $schema, $post_id);
        
        $this->logger->info('Schema injected', [
            'post_id' => $post_id,
            'schema_type' => $schema['@type'] ?? 'Unknown'
        ]);
    }
}
```

**1.3 创建 AJAX 处理类** (`includes/class-ajax-handler.php`)

```php
<?php
/**
 * AJAX Handler Class
 *
 * @package Schema_Validator_Pro
 * @since 2.0.0
 */

namespace SchemaValidatorPro;

class AJAX_Handler {
    private $api_client;
    private $cache_manager;
    private $logger;
    
    public function __construct($api_client, $cache_manager, $logger) {
        $this->api_client = $api_client;
        $this->cache_manager = $cache_manager;
        $this->logger = $logger;
    }
    
    public function init() {
        add_action('wp_ajax_svp_generate_schema', [$this, 'generate_schema']);
    }
    
    public function generate_schema() {
        $start_time = microtime(true);
        
        // Validate request
        $validation = $this->validate_request();
        if (is_wp_error($validation)) {
            $this->send_error($validation);
            return;
        }
        
        $post_id = $validation['post_id'];
        $schema_type = $validation['schema_type'];
        $force = $validation['force'];
        
        // Try cache first
        if (!$force) {
            $cached = $this->cache_manager->get($post_id, $schema_type);
            if ($cached !== false) {
                $this->send_success($cached, true, $start_time);
                return;
            }
        }
        
        // Generate via API
        $result = $this->api_client->generate_schema($post_id, $schema_type);
        
        if (is_wp_error($result)) {
            // Try cache fallback
            $cached = $this->cache_manager->get($post_id, $schema_type);
            if ($cached !== false) {
                $this->send_success($cached, true, $start_time, true);
                return;
            }
            
            $this->send_error($result);
            return;
        }
        
        // Save and cache
        $this->save_schema($post_id, $schema_type, $result);
        $this->cache_manager->set($post_id, $schema_type, $result);
        
        $this->send_success($result, false, $start_time);
    }
    
    private function validate_request() {
        check_ajax_referer('svp_generate_schema');
        
        $post_id = isset($_POST['post_id']) ? intval($_POST['post_id']) : 0;
        if (!$post_id) {
            return new \WP_Error('invalid_post_id', __('Invalid post ID', 'schema-validator-pro'));
        }
        
        if (!current_user_can('edit_post', $post_id)) {
            return new \WP_Error('permission_denied', __('Permission denied', 'schema-validator-pro'));
        }
        
        $post = get_post($post_id);
        if (!$post) {
            return new \WP_Error('post_not_found', __('Post not found', 'schema-validator-pro'));
        }
        
        return [
            'post_id' => $post_id,
            'schema_type' => isset($_POST['schema_type']) ? sanitize_text_field($_POST['schema_type']) : 'Article',
            'force' => isset($_POST['force']) && $_POST['force'] === 'true'
        ];
    }
    
    private function save_schema($post_id, $schema_type, $schema) {
        update_post_meta($post_id, '_svp_schema', wp_json_encode($schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
        update_post_meta($post_id, '_svp_schema_type', $schema_type);
        update_post_meta($post_id, '_svp_schema_generated_at', current_time('mysql'));
        update_post_meta($post_id, '_svp_schema_version', SVP_VERSION);
        
        do_action('svp_schema_generated', $schema, $post_id);
    }
    
    private function send_success($schema, $cached, $start_time, $fallback = false) {
        $duration_ms = round((microtime(true) - $start_time) * 1000, 2);
        
        $this->logger->info('Schema generation successful', [
            'cached' => $cached,
            'fallback' => $fallback,
            'duration_ms' => $duration_ms
        ]);
        
        wp_send_json_success([
            'schema' => $schema,
            'cached' => $cached,
            'fallback' => $fallback,
            'message' => $this->get_success_message($cached, $fallback)
        ]);
    }
    
    private function send_error($error) {
        $this->logger->error('Schema generation failed', [
            'error' => $error->get_error_message()
        ]);
        
        wp_send_json_error($error->get_error_message());
    }
    
    private function get_success_message($cached, $fallback) {
        if ($fallback) {
            return __('API unavailable. Using cached schema.', 'schema-validator-pro');
        }
        if ($cached) {
            return __('Schema retrieved from cache', 'schema-validator-pro');
        }
        return __('Schema generated successfully!', 'schema-validator-pro');
    }
}
```

#### 阶段 2: 迁移现有功能（第 3-4 周）

**任务清单**:
- [ ] 创建 Cache_Manager 类
- [ ] 创建 API_Client 类
- [ ] 创建 Admin_UI 类
- [ ] 创建 Meta_Box 类
- [ ] 创建 Settings 类
- [ ] 迁移所有函数到类方法
- [ ] 更新测试用例

#### 阶段 3: 添加新功能（第 5-6 周）

**新功能**:
1. **REST API 支持**
2. **Gutenberg 块**
3. **Schema 预览**
4. **批量生成**
5. **导入/导出**

#### 阶段 4: 测试和优化（第 7-8 周）

**任务**:
- [ ] 完整回归测试
- [ ] 性能测试
- [ ] 安全审计
- [ ] 文档更新
- [ ] Beta 测试

---

## 📈 预期收益

### 代码质量提升

| 指标 | v1.0.0 | v2.0.0 | 改进 |
|------|--------|--------|------|
| 主文件行数 | 761 | <100 | -87% |
| 平均函数长度 | 45 行 | <20 行 | -56% |
| 圈复杂度 | 15 | <5 | -67% |
| 代码重复率 | 15% | <5% | -67% |
| 测试覆盖率 | 87% | >95% | +9% |

### 可维护性提升

- ✅ 单一职责原则
- ✅ 依赖注入
- ✅ 接口隔离
- ✅ 命名空间
- ✅ 自动加载

### 性能提升

- ✅ 对象缓存支持
- ✅ 延迟加载
- ✅ 查询优化
- ✅ 资源压缩

---

## 🎯 成功标准

### 代码质量
- [ ] 所有类遵循 SOLID 原则
- [ ] 平均函数长度 <20 行
- [ ] 圈复杂度 <5
- [ ] 代码重复率 <5%

### 测试
- [ ] 单元测试覆盖率 >95%
- [ ] 集成测试覆盖率 >80%
- [ ] 所有测试通过

### 性能
- [ ] 页面加载时间 <100ms
- [ ] API 响应时间 <500ms
- [ ] 缓存命中率 >80%

### 兼容性
- [ ] WordPress 5.0+
- [ ] PHP 7.4+
- [ ] 主流主题兼容
- [ ] 主流插件兼容

---

**准备开始重构之旅！** 🚀

