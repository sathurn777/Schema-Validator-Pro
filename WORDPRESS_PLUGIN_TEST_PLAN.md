# WordPress 插件测试计划 - 严格执行版

**创建日期**: 2025-10-22  
**态度**: 严格、刻薄、认真、诚实  
**目标**: 真实的 80%+ 测试覆盖率  
**验证方式**: 运行 PHPUnit 并查看覆盖率报告

---

## 📊 当前状态（诚实的）

| 文件 | 代码行数 | 测试数量 | 覆盖率 | 状态 |
|------|---------|---------|--------|------|
| `schema-validator-pro.php` | 761 行 | **0** | **0%** | ❌ 未测试 |
| `includes/class-logger.php` | 310 行 | **0** | **0%** | ❌ 未测试 |
| `assets/admin/js/metabox.js` | 169 行 | **0** | **0%** | ❌ 未测试 |
| **总计** | **1240 行** | **0** | **0%** | ❌ **完全未测试** |

---

## 🎯 测试目标（必须达到）

| 文件 | 目标覆盖率 | 最少测试数 | 优先级 |
|------|-----------|-----------|--------|
| `schema-validator-pro.php` | **80%+** | **40+** | P0 |
| `includes/class-logger.php` | **80%+** | **15+** | P1 |
| `assets/admin/js/metabox.js` | **80%+** | **10+** | P2 |
| **总计** | **80%+** | **65+** | - |

---

## 📋 函数清单（schema-validator-pro.php）

### 核心功能函数（P0 - 必须 100% 覆盖）

1. **`svp_inject_schema()`** - 核心注入函数
   - 测试场景：
     - ✅ 在单篇文章页面注入 Schema
     - ✅ 在单页面注入 Schema
     - ✅ 在首页不注入（`!is_singular()`）
     - ✅ 在归档页不注入
     - ✅ 无 Schema 时不注入
     - ✅ Schema 为空字符串时不注入
     - ✅ Schema 为 JSON 字符串时正确解码
     - ✅ Schema 为数组时直接使用
     - ✅ 已存在 Schema 时不重复注入
     - ✅ 触发 `svp_schema_data` filter
     - ✅ 触发 `svp_before_schema_injection` action
     - ✅ 触发 `svp_after_schema_injection` action
     - ✅ 输出正确的 HTML 注释
     - ✅ 使用 `wp_json_encode` 安全输出
   - **最少测试数**: 14 个

2. **`svp_has_existing_schema()`** - 重复检测
   - 测试场景：
     - ✅ 默认返回 false
     - ✅ 触发 `svp_has_existing_schema` filter
     - ✅ Filter 返回 true 时返回 true
   - **最少测试数**: 3 个

3. **`svp_ajax_generate_schema()`** - AJAX 处理（最复杂）
   - 测试场景：
     - ✅ Nonce 验证失败时返回错误
     - ✅ 无效 post_id 时返回错误
     - ✅ post_id = 0 时返回错误
     - ✅ 无权限时返回错误（`!current_user_can('edit_post')`）
     - ✅ Post 不存在时返回错误
     - ✅ 成功从缓存获取 Schema
     - ✅ 缓存未命中时调用 API
     - ✅ API 未配置时尝试缓存降级
     - ✅ API 未配置且无缓存时返回错误
     - ✅ API 调用成功时保存 Schema
     - ✅ API 调用成功时更新 post meta（4 个字段）
     - ✅ API 调用成功时缓存 Schema
     - ✅ API 调用成功时触发 `svp_schema_generated` action
     - ✅ 网络错误时尝试缓存降级
     - ✅ 网络错误且无缓存时返回错误
     - ✅ 5xx 错误时尝试缓存降级
     - ✅ 5xx 错误且无缓存时返回错误
     - ✅ 4xx 错误时直接返回错误（不降级）
     - ✅ 无效 API 响应时返回错误
     - ✅ 触发所有 filters（`svp_api_endpoint`, `svp_schema_metadata`, `svp_api_request_body`, `svp_api_sslverify`）
     - ✅ 正确添加 API Key header
     - ✅ 正确记录日志
   - **最少测试数**: 22 个

### 缓存函数（P0 - 必须 100% 覆盖）

4. **`svp_get_schema_cache_key()`** - 缓存键生成
   - 测试场景：
     - ✅ 正确生成缓存键格式
     - ✅ 不同 post_id 生成不同键
     - ✅ 不同 schema_type 生成不同键
   - **最少测试数**: 3 个

5. **`svp_get_cached_schema()`** - 获取缓存
   - 测试场景：
     - ✅ 缓存存在时返回数据
     - ✅ 缓存不存在时返回 false
   - **最少测试数**: 2 个

6. **`svp_set_cached_schema()`** - 设置缓存
   - 测试场景：
     - ✅ 成功设置缓存
     - ✅ 使用正确的过期时间
     - ✅ 默认过期时间为 3600 秒
   - **最少测试数**: 3 个

7. **`svp_clear_cached_schema()`** - 清除缓存
   - 测试场景：
     - ✅ 清除指定类型的缓存
     - ✅ 清除所有类型的缓存（schema_type = null）
   - **最少测试数**: 2 个

8. **`svp_clear_cache_on_post_update()`** - 自动清除缓存
   - 测试场景：
     - ✅ Post 更新时清除缓存
   - **最少测试数**: 1 个

### 管理界面函数（P1 - 至少 80% 覆盖）

9. **`svp_enqueue_admin_assets()`** - 加载资源
   - 测试场景：
     - ✅ 在 post.php 页面加载资源
     - ✅ 在 post-new.php 页面加载资源
     - ✅ 在其他页面不加载
     - ✅ 正确 localize script
   - **最少测试数**: 4 个

10. **`svp_enqueue_admin_page_assets()`** - 加载管理页资源
    - 测试场景：
      - ✅ 在插件页面加载资源
      - ✅ 在其他页面不加载
    - **最少测试数**: 2 个

11. **`svp_check_api_status()`** - API 状态检查
    - 测试场景：
      - ✅ Endpoint 为空时返回错误
      - ✅ API 可用时返回成功
      - ✅ API 不可用时返回错误
      - ✅ 网络错误时返回错误信息
      - ✅ HTTP 非 200 时返回错误
    - **最少测试数**: 5 个

### 其他函数（P2 - 至少 60% 覆盖）

12. **`svp_load_textdomain()`** - 国际化
13. **`svp_add_meta_box()`** - 添加 Meta Box
14. **`svp_schema_metabox_callback()`** - Meta Box 渲染
15. **`svp_add_admin_menu()`** - 添加菜单
16. **`svp_register_settings()`** - 注册设置
17. **`svp_settings_page()`** - 设置页面
18. **`svp_admin_page()`** - 管理页面

---

## 🔧 测试环境设置

### 1. 安装 PHPUnit

```bash
cd wordpress-plugin/schema-validator-pro

# 检查是否已安装 Composer
composer --version || echo "需要安装 Composer"

# 初始化 Composer（如果没有 composer.json）
composer init --no-interaction

# 安装 PHPUnit 和 WordPress 测试库
composer require --dev phpunit/phpunit:^9.0
composer require --dev yoast/phpunit-polyfills
composer require --dev wp-phpunit/wp-phpunit
```

### 2. 创建 PHPUnit 配置文件

**文件**: `phpunit.xml.dist`

```xml
<?xml version="1.0"?>
<phpunit
    bootstrap="tests/bootstrap.php"
    backupGlobals="false"
    colors="true"
    convertErrorsToExceptions="true"
    convertNoticesToExceptions="true"
    convertWarningsToExceptions="true"
>
    <testsuites>
        <testsuite name="Schema Validator Pro Test Suite">
            <directory>./tests/</directory>
        </testsuite>
    </testsuites>
    <coverage processUncoveredFiles="true">
        <include>
            <directory suffix=".php">./</directory>
        </include>
        <exclude>
            <directory>./tests/</directory>
            <directory>./vendor/</directory>
            <directory>./assets/</directory>
        </exclude>
        <report>
            <html outputDirectory="tests/coverage"/>
            <text outputFile="php://stdout" showUncoveredFiles="true"/>
        </report>
    </coverage>
</phpunit>
```

### 3. 创建测试引导文件

**文件**: `tests/bootstrap.php`

---

## 📝 测试文件结构

```
wordpress-plugin/schema-validator-pro/
├── tests/
│   ├── bootstrap.php                    # PHPUnit 引导文件
│   ├── test-injection.php               # 测试 Schema 注入（14 个测试）
│   ├── test-ajax.php                    # 测试 AJAX 处理（22 个测试）
│   ├── test-cache.php                   # 测试缓存机制（11 个测试）
│   ├── test-admin-assets.php            # 测试资源加载（6 个测试）
│   ├── test-api-status.php              # 测试 API 状态（5 个测试）
│   ├── test-logger.php                  # 测试日志类（15 个测试）
│   └── coverage/                        # 覆盖率报告（自动生成）
├── phpunit.xml.dist                     # PHPUnit 配置
└── composer.json                        # Composer 依赖
```

**总测试数**: 73 个（超过目标 65 个）

---

## ✅ 验收标准（严格的）

### 必须通过的检查

1. **运行所有测试**
   ```bash
   cd wordpress-plugin/schema-validator-pro
   vendor/bin/phpunit
   ```
   - ✅ 所有测试通过（0 failed）
   - ✅ 至少 65 个测试
   - ✅ 无 warnings 或 errors

2. **检查覆盖率**
   ```bash
   vendor/bin/phpunit --coverage-text
   ```
   - ✅ `schema-validator-pro.php` 覆盖率 ≥ 80%
   - ✅ `includes/class-logger.php` 覆盖率 ≥ 80%
   - ✅ 总体覆盖率 ≥ 80%

3. **查看详细覆盖率报告**
   ```bash
   vendor/bin/phpunit --coverage-html tests/coverage
   open tests/coverage/index.html
   ```
   - ✅ 查看每个文件的覆盖率
   - ✅ 查看未覆盖的代码行
   - ✅ 确认关键函数 100% 覆盖

4. **代码质量检查**
   ```bash
   # 检查 PHP 语法
   find . -name "*.php" -not -path "./vendor/*" -exec php -l {} \;
   
   # 检查 WordPress 编码标准（可选）
   composer require --dev wp-coding-standards/wpcs
   vendor/bin/phpcs --standard=WordPress schema-validator-pro.php
   ```

---

## 🚨 严格的执行要求

### 不允许的行为

1. ❌ **不允许降低测试标准** - 必须达到 80% 覆盖率
2. ❌ **不允许跳过测试** - 所有测试必须通过
3. ❌ **不允许虚假覆盖率** - 必须运行 `--coverage-text` 验证
4. ❌ **不允许注释掉失败的测试** - 必须修复
5. ❌ **不允许使用 `@codeCoverageIgnore`** - 除非有充分理由

### 必须做的事

1. ✅ **每个测试必须有明确的断言** - 不能只调用函数不验证结果
2. ✅ **每个测试必须独立** - 不能依赖其他测试的状态
3. ✅ **每个测试必须清理环境** - 使用 `tearDown()` 清理
4. ✅ **每个测试必须有描述性名称** - `test_inject_schema_on_single_post()`
5. ✅ **每个测试必须测试一个场景** - 不要在一个测试中测试多个场景

---

## 📊 进度跟踪

### P0 任务（必须完成）

- [ ] 创建测试环境（PHPUnit + WordPress Test Library）
- [ ] 创建 `tests/bootstrap.php`
- [ ] 创建 `tests/test-injection.php`（14 个测试）
- [ ] 创建 `tests/test-ajax.php`（22 个测试）
- [ ] 创建 `tests/test-cache.php`（11 个测试）
- [ ] 运行测试并验证全部通过
- [ ] 运行覆盖率检查并验证 ≥ 80%

### P1 任务（强烈建议）

- [ ] 创建 `tests/test-admin-assets.php`（6 个测试）
- [ ] 创建 `tests/test-api-status.php`（5 个测试）
- [ ] 创建 `tests/test-logger.php`（15 个测试）
- [ ] 运行完整测试套件
- [ ] 生成 HTML 覆盖率报告

### P2 任务（可选）

- [ ] JavaScript 测试（Jest/Mocha）
- [ ] 集成测试（真实 WordPress 环境）
- [ ] 性能测试
- [ ] 安全测试

---

## 🎯 成功标准

### 最终验收

运行以下命令并截图：

```bash
cd wordpress-plugin/schema-validator-pro

# 1. 运行所有测试
vendor/bin/phpunit

# 2. 查看覆盖率
vendor/bin/phpunit --coverage-text

# 3. 生成 HTML 报告
vendor/bin/phpunit --coverage-html tests/coverage
```

**必须看到**:
- ✅ `OK (73 tests, XXX assertions)` 或更多
- ✅ `schema-validator-pro.php ... 80.XX%` 或更高
- ✅ `includes/class-logger.php ... 80.XX%` 或更高
- ✅ `TOTAL ... 80.XX%` 或更高

**不允许看到**:
- ❌ `FAILURES!`
- ❌ `ERRORS!`
- ❌ `Coverage: XX.XX%` 低于 80%
- ❌ `Risky tests`
- ❌ `Incomplete tests`

---

**创建人**: AI Assistant  
**态度**: 严格、刻薄、认真、诚实  
**目标**: 真实的 80%+ 覆盖率  
**验证**: 必须运行 PHPUnit 并查看覆盖率报告

