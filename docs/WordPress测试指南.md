# WordPress 测试指南

本指南提供完整的 WordPress 环境测试步骤，用于验证 Schema Validator Pro 插件的所有功能。

---

## 📋 测试环境

### 方式 1: Docker Compose（推荐）

使用 Docker Compose 一键启动完整测试环境（WordPress + MySQL + 后端 API）。

#### 前置要求

- Docker Desktop 已安装并运行
- 端口 8080（WordPress）和 8000（后端 API）未被占用

#### 启动环境

```bash
cd schema-validator-pro_副本2

# 启动所有服务
docker-compose -f docker-compose.test.yml up -d

# 查看服务状态
docker-compose -f docker-compose.test.yml ps

# 查看日志
docker-compose -f docker-compose.test.yml logs -f
```

**预期输出**:
```
NAME              IMAGE              STATUS         PORTS
svp-wordpress     wordpress:latest   Up (healthy)   0.0.0.0:8080->80/tcp
svp-backend       svp-backend        Up (healthy)   0.0.0.0:8000->8000/tcp
svp-mysql         mysql:8.0          Up (healthy)   3306/tcp
```

#### 访问地址

- **WordPress 前台**: http://localhost:8080
- **WordPress 后台**: http://localhost:8080/wp-admin
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

#### 停止环境

```bash
# 停止服务
docker-compose -f docker-compose.test.yml down

# 停止并删除数据卷（重置环境）
docker-compose -f docker-compose.test.yml down -v
```

---

### 方式 2: 本地 WordPress

如果已有本地 WordPress 环境（XAMPP、MAMP、Local by Flywheel 等）。

#### 安装插件

```bash
# 复制插件到 WordPress 插件目录
cp -r wordpress-plugin/schema-validator-pro /path/to/wordpress/wp-content/plugins/

# 或创建符号链接（推荐，便于开发）
ln -s $(pwd)/wordpress-plugin/schema-validator-pro /path/to/wordpress/wp-content/plugins/schema-validator-pro
```

#### 启动后端 API

```bash
cd schema-validator-pro_副本2

# 安装依赖
pip install -r config/requirements.txt

# 启动服务
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 测试步骤

### 1. WordPress 初始化

#### 1.1 安装 WordPress

1. 访问 http://localhost:8080
2. 选择语言（中文或英文）
3. 填写站点信息：
   - **站点标题**: Schema Validator Pro Test
   - **用户名**: admin
   - **密码**: admin（或自定义强密码）
   - **邮箱**: admin@example.com
4. 点击"安装 WordPress"
5. 登录后台

#### 1.2 激活插件

1. 导航到 **插件** > **已安装的插件**
2. 找到 **Schema Validator Pro**
3. 点击 **激活**

**预期结果**:
- ✅ 插件激活成功，无错误提示
- ✅ 左侧菜单出现 **Schema Pro** 菜单项

---

### 2. 配置后端 API

#### 2.1 访问设置页面

1. 点击左侧菜单 **Schema Pro** > **Settings**
2. 在 **API Endpoint** 字段输入：
   - Docker 环境: `http://backend:8000`
   - 本地环境: `http://localhost:8000`
3. 点击 **Save Settings**

**预期结果**:
- ✅ 显示 "Settings saved successfully!" 成功消息
- ✅ **API Status** 显示绿色 ✓ "API is available"

#### 2.2 验证 API 连接

如果 API 状态显示红色 ✗，检查：

```bash
# 测试后端 API 健康检查
curl http://localhost:8000/health

# 预期输出
{
  "status": "healthy",
  "supported_types": ["Article", "Product", "Recipe", ...]
}
```

**常见问题**:
- **Docker 环境**: 确保使用 `http://backend:8000`（容器内部网络）
- **本地环境**: 确保后端服务已启动且使用 `http://localhost:8000`
- **CORS 错误**: 后端已配置允许所有来源，不应出现 CORS 问题

---

### 3. 生成 Schema

#### 3.1 创建测试文章

1. 导航到 **文章** > **写文章**
2. 填写文章内容：

**标题**: 如何使用 Schema.org 提升 SEO

**内容**:
```
Schema.org 是一种结构化数据标记语言，可以帮助搜索引擎更好地理解网页内容。

本文将介绍如何在 WordPress 中使用 Schema Validator Pro 插件自动生成和注入 Schema.org 标记。

## 什么是 Schema.org？

Schema.org 是由 Google、Microsoft、Yahoo 和 Yandex 共同创建的结构化数据词汇表。

## 为什么需要 Schema.org？

1. 提升搜索引擎可见性
2. 获得富媒体搜索结果
3. 提高点击率

## 如何使用？

使用 Schema Validator Pro 插件，只需点击一次即可自动生成符合规范的 Schema 标记。
```

3. 点击 **发布**

#### 3.2 生成 Schema

1. 在文章编辑页面，找到右侧边栏的 **Schema Validator Pro** meta box
2. 在 **Schema Type** 下拉菜单中选择 **Article**
3. 点击 **Generate Schema** 按钮

**预期结果**:
- ✅ 按钮文本变为 "Generating..."
- ✅ 显示加载状态消息 "Generating schema..."
- ✅ 1-3 秒后显示绿色成功消息 "✓ Schema generated successfully!"
- ✅ 页面自动刷新
- ✅ Meta box 显示生成的 Schema 信息：
  - **Status**: ✓ Schema generated
  - **Type**: Article
  - **Generated**: 2025-10-21 14:30:00
  - **View Schema JSON** 可展开查看

#### 3.3 查看生成的 Schema

点击 **View Schema JSON** 展开，应该看到类似：

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "如何使用 Schema.org 提升 SEO",
  "author": {
    "@type": "Person",
    "name": "admin"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Schema Validator Pro Test",
    "logo": {
      "@type": "ImageObject",
      "url": "http://localhost:8080/wp-content/uploads/..."
    }
  },
  "datePublished": "2025-10-21T14:30:00+00:00",
  "dateModified": "2025-10-21T14:30:00+00:00",
  "description": "Schema.org 是一种结构化数据标记语言...",
  "image": [...]
}
```

**验证要点**:
- ✅ `@context` 为 `https://schema.org`
- ✅ `@type` 为 `Article`
- ✅ `headline` 为文章标题
- ✅ `author` 为嵌套的 `Person` 对象（带 `@type`）
- ✅ `publisher` 为嵌套的 `Organization` 对象（带 `logo` ImageObject）
- ✅ `datePublished` 为 ISO 8601 格式
- ✅ JSON 格式正确，无语法错误

---

### 4. 验证前端注入

#### 4.1 访问文章页面

1. 点击文章编辑页面顶部的 **查看文章** 或 **预览**
2. 在新标签页打开文章

#### 4.2 查看页面源代码

1. 右键点击页面 > **查看页面源代码**（或按 `Ctrl+U` / `Cmd+Option+U`）
2. 搜索 `Schema Validator Pro`（`Ctrl+F` / `Cmd+F`）

**预期结果**:

应该在 `<head>` 部分找到：

```html
<!-- Schema Validator Pro v1.0.0 -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "如何使用 Schema.org 提升 SEO",
  ...
}
</script>
<!-- /Schema Validator Pro -->
```

**验证要点**:
- ✅ 注释包含插件名称和版本号
- ✅ `<script type="application/ld+json">` 标签正确
- ✅ JSON 内容与 meta box 中显示的一致
- ✅ 只有一个 Schema Validator Pro 注入的 script（无重复）

---

### 5. Google Rich Results 测试

#### 5.1 使用 Google 工具验证

1. 复制文章的完整 URL（如 `http://localhost:8080/2025/10/21/how-to-use-schema/`）
2. 访问 https://search.google.com/test/rich-results
3. 选择 **URL** 标签
4. 粘贴 URL 并点击 **测试 URL**

**注意**: 本地环境（localhost）无法被 Google 访问，需要使用以下替代方案：

#### 5.2 使用代码片段测试（推荐）

1. 访问 https://search.google.com/test/rich-results
2. 选择 **代码** 标签
3. 复制页面源代码中的 JSON-LD script 内容
4. 粘贴到测试工具并点击 **测试代码**

**预期结果**:
- ✅ 显示 "页面符合富媒体搜索结果的条件"
- ✅ 检测到的项目类型: **Article**
- ✅ 无错误或警告
- ✅ 所有必填字段都已填充

#### 5.3 使用 Schema.org Validator

1. 访问 https://validator.schema.org/
2. 粘贴 JSON-LD 代码
3. 点击 **RUN TEST**

**预期结果**:
- ✅ 显示绿色 "No errors found"
- ✅ Schema 类型正确识别
- ✅ 所有字段符合 schema.org 规范

---

### 6. 测试其他 Schema 类型

重复步骤 3-5，测试其他 Schema 类型：

#### 6.1 Product Schema

**文章标题**: iPhone 15 Pro 评测  
**Schema Type**: Product  
**预期字段**: name, description, brand, offers (带 @type: Offer)

#### 6.2 Recipe Schema

**文章标题**: 红烧肉的做法  
**Schema Type**: Recipe  
**预期字段**: name, recipeIngredient, recipeInstructions (带 @type: HowToStep)

#### 6.3 HowTo Schema

**文章标题**: 如何更换汽车轮胎  
**Schema Type**: HowTo  
**预期字段**: name, step (带 @type: HowToStep)

#### 6.4 FAQPage Schema

**文章标题**: WordPress 常见问题  
**Schema Type**: FAQPage  
**预期字段**: mainEntity (带 @type: Question)

---

### 7. 错误处理测试

#### 7.1 测试后端不可用

1. 停止后端 API 服务：
   ```bash
   # Docker 环境
   docker-compose -f docker-compose.test.yml stop backend
   
   # 本地环境
   # 按 Ctrl+C 停止 uvicorn
   ```

2. 在 WordPress 中尝试生成 Schema

**预期结果**:
- ✅ 显示红色错误消息 "✗ Network error: ..."
- ✅ 按钮恢复为 "Generate Schema"
- ✅ 不会导致 WordPress 崩溃或白屏

3. 重新启动后端服务：
   ```bash
   docker-compose -f docker-compose.test.yml start backend
   ```

#### 7.2 测试权限检查

1. 创建一个 **编辑者** 角色的用户
2. 以该用户登录
3. 尝试访问 **Schema Pro** > **Settings**

**预期结果**:
- ✅ 无法访问设置页面（显示权限错误）
- ✅ 可以在文章编辑页面生成 Schema（编辑者有 edit_post 权限）

#### 7.3 测试重复注入防护

1. 生成 Schema 后，多次刷新文章前端页面
2. 查看页面源代码

**预期结果**:
- ✅ 只有一个 `<!-- Schema Validator Pro -->` 注释块
- ✅ 只有一个 JSON-LD script 标签

---

### 8. 性能测试

#### 8.1 测试资源加载

1. 打开文章编辑页面
2. 打开浏览器开发者工具（F12）
3. 切换到 **Network** 标签
4. 刷新页面

**预期结果**:
- ✅ `metabox.css` 加载成功（200 OK）
- ✅ `metabox.js` 加载成功（200 OK）
- ✅ 文件大小合理（CSS < 5KB, JS < 10KB）
- ✅ 无 404 错误

#### 8.2 测试 AJAX 性能

1. 在开发者工具的 **Network** 标签中
2. 点击 **Generate Schema** 按钮
3. 观察 `admin-ajax.php` 请求

**预期结果**:
- ✅ 请求完成时间 < 5 秒
- ✅ 响应状态 200 OK
- ✅ 响应包含 `success: true` 和 schema 数据

---

### 9. 兼容性测试

#### 9.1 测试 Gutenberg 编辑器

1. 确保使用 Gutenberg（块编辑器）
2. 创建新文章
3. 生成 Schema

**预期结果**:
- ✅ Meta box 正常显示在侧边栏
- ✅ 功能正常工作

#### 9.2 测试经典编辑器

1. 安装 **Classic Editor** 插件
2. 激活插件
3. 创建新文章
4. 生成 Schema

**预期结果**:
- ✅ Meta box 正常显示在侧边栏
- ✅ 功能正常工作

---

## ✅ 测试清单

完成所有测试后，使用此清单验证：

| 测试项 | 状态 | 备注 |
|--------|------|------|
| **环境启动** |  |  |
| Docker Compose 启动成功 | ⬜ |  |
| WordPress 可访问 | ⬜ |  |
| 后端 API 可访问 | ⬜ |  |
| **插件安装** |  |  |
| 插件激活成功 | ⬜ |  |
| 菜单项出现 | ⬜ |  |
| **API 配置** |  |  |
| 设置保存成功 | ⬜ |  |
| API 状态显示可用 | ⬜ |  |
| **Schema 生成** |  |  |
| Article Schema 生成成功 | ⬜ |  |
| Product Schema 生成成功 | ⬜ |  |
| Recipe Schema 生成成功 | ⬜ |  |
| HowTo Schema 生成成功 | ⬜ |  |
| FAQPage Schema 生成成功 | ⬜ |  |
| **前端注入** |  |  |
| JSON-LD 出现在 head | ⬜ |  |
| 格式正确 | ⬜ |  |
| 无重复注入 | ⬜ |  |
| **验证工具** |  |  |
| Google Rich Results 通过 | ⬜ |  |
| Schema.org Validator 通过 | ⬜ |  |
| **错误处理** |  |  |
| 后端不可用时显示错误 | ⬜ |  |
| 权限检查正常 | ⬜ |  |
| **性能** |  |  |
| 资源加载正常 | ⬜ |  |
| AJAX 响应时间 < 5s | ⬜ |  |
| **兼容性** |  |  |
| Gutenberg 编辑器兼容 | ⬜ |  |
| 经典编辑器兼容 | ⬜ |  |

---

## 🐛 常见问题

### 问题 1: API 状态显示不可用

**原因**: 后端服务未启动或网络配置错误

**解决方案**:
```bash
# 检查后端服务状态
docker-compose -f docker-compose.test.yml ps backend

# 查看后端日志
docker-compose -f docker-compose.test.yml logs backend

# 测试健康检查
curl http://localhost:8000/health
```

### 问题 2: 生成 Schema 时显示网络错误

**原因**: WordPress 无法访问后端 API

**解决方案**:
- Docker 环境: 确保使用 `http://backend:8000`（容器名称）
- 本地环境: 确保使用 `http://localhost:8000`
- 检查防火墙设置

### 问题 3: 前端页面没有 JSON-LD

**原因**: Schema 未生成或注入失败

**解决方案**:
1. 确认 meta box 显示 "Schema generated"
2. 检查 post meta: `SELECT * FROM wp_postmeta WHERE meta_key LIKE '_svp_%';`
3. 查看 WordPress 调试日志

### 问题 4: CSS/JS 文件 404

**原因**: 文件路径错误或权限问题

**解决方案**:
```bash
# 检查文件是否存在
ls -la wordpress-plugin/schema-validator-pro/assets/admin/

# 检查文件权限
chmod -R 755 wordpress-plugin/schema-validator-pro/assets/
```

---

## 📊 测试报告模板

完成测试后，填写此报告：

```markdown
# Schema Validator Pro 测试报告

**测试日期**: 2025-10-21  
**测试环境**: Docker Compose / 本地 WordPress  
**WordPress 版本**: 6.4  
**PHP 版本**: 8.1  
**测试人员**: [姓名]

## 测试结果

- **通过**: X / 25
- **失败**: X / 25
- **跳过**: X / 25

## 发现的问题

1. [问题描述]
   - **严重程度**: 高/中/低
   - **复现步骤**: ...
   - **预期结果**: ...
   - **实际结果**: ...

## 建议

1. [改进建议]

## 结论

[总体评价]
```

---

**测试完成后，请将结果反馈给开发团队！**

