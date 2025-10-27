# Schema Validator Pro - API 参考文档

> **版本**: 1.0.0
> **测试覆盖率**: 97% (569/569 tests)
> **性能**: 微秒级响应时间（275,000+ ops/sec）
> **生产状态**: ✅ Production Ready

## 目录

- [1. 基础信息](#1-基础信息)
- [2. 认证](#2-认证)
- [3. 端点列表](#3-端点列表)
- [4. 支持的 Schema 类型](#4-支持的-schema-类型)
- [5. 数据模型](#5-数据模型)
- [6. 错误码](#6-错误码)
- [7. 代码示例](#7-代码示例)
- [8. 性能指标](#8-性能指标)

---

## 1. 基础信息

### 1.1 Base URL

```
http://localhost:8000
```

生产环境请替换为实际域名。

### 1.2 Content-Type

所有 POST 请求必须使用：

```
Content-Type: application/json
```

### 1.3 响应格式

所有响应均为 JSON 格式。

### 1.4 HTTP 状态码

| 状态码 | 说明 |
|-------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（API Key 无效） |
| 404 | 资源不存在 |
| 413 | 请求体过大 |
| 422 | 验证错误（Pydantic） |
| 500 | 服务器内部错误 |

---

## 2. 认证

### 2.1 API Key 认证（可选）

如果服务器配置了 `API_KEY` 环境变量，所有请求必须包含 API Key。

**请求头**：

```
X-API-Key: your-secret-key
```

**示例**：

```bash
curl -H "X-API-Key: your-secret-key" \
  http://localhost:8000/api/v1/schema/types
```

### 2.2 WordPress 认证

WordPress 集成使用 Application Password 认证（HTTP Basic Auth）。

**配置步骤**：

1. WordPress 后台 → 用户 → 个人资料
2. 滚动到 Application Passwords 部分
3. 创建新密码
4. 在请求中使用 `username` 和 `app_password`

---

## 3. 端点列表

### 端点总览

| 端点 | 方法 | 功能 | 性能 |
|-----|------|------|------|
| `/` | GET | 健康检查 | < 1ms |
| `/api/v1/schema/generate` | POST | 生成 Schema | < 5ms |
| `/api/v1/schema/validate` | POST | 验证 Schema | < 3ms |
| `/api/v1/schema/types` | GET | 获取支持的类型列表 | < 1ms |
| `/api/v1/schema/template/{type}` | GET | 获取 Schema 模板 | < 1ms |
| `/metrics` | GET | Prometheus 指标 | < 1ms |

---

### 3.1 健康检查

#### GET /

**描述**：简单健康检查

**请求**：

```bash
curl http://localhost:8000/
```

**响应**：

```json
{
  "status": "ok",
  "service": "Schema Validator Pro",
  "version": "1.0.0"
}
```

---

#### GET /health

**描述**：详细健康检查

**请求**：

```bash
curl http://localhost:8000/health
```

**响应**：

```json
{
  "status": "healthy",
  "services": {
    "schema_generator": "ok",
    "schema_validator": "ok"
  },
  "supported_types": [
    "Article", "Product", "Recipe", "Event",
    "Organization", "Person", "FAQPage", "HowTo", "Course"
  ]
}
```

---

### 3.2 指标

#### GET /metrics

**描述**：Prometheus 指标端点

**请求**：

```bash
curl http://localhost:8000/metrics
```

**响应**：Prometheus 文本格式

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/health",status="200"} 42
...
```

---

### 3.3 Schema 类型

#### GET /api/v1/schema/types

**描述**：获取支持的 Schema 类型列表

**请求**：

```bash
curl http://localhost:8000/api/v1/schema/types
```

**响应**：

```json
{
  "types": [
    "Article",
    "Product",
    "Recipe",
    "Event",
    "Organization",
    "Person",
    "FAQPage",
    "HowTo",
    "Course"
  ]
}
```

---

### 3.4 Schema 模板

#### GET /api/v1/schema/template/{schema_type}

**描述**：获取指定类型的空 Schema 模板

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| schema_type | string | 是 | Schema 类型（如 Article） |

**请求**：

```bash
curl http://localhost:8000/api/v1/schema/template/Article
```

**响应**：

```json
{
  "schema": {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "",
    "datePublished": "",
    "author": {
      "@type": "Person",
      "name": ""
    }
  }
}
```

**错误响应（404）**：

```json
{
  "error_code": "INVALID_SCHEMA_TYPE",
  "message": "Unsupported schema type: InvalidType",
  "details": {
    "schema_type": "InvalidType",
    "supported_types": ["Article", "Product", ...]
  }
}
```

---

### 3.5 生成 Schema

#### POST /api/v1/schema/generate

**描述**：基于内容自动生成 Schema.org JSON-LD

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|-----|------|------|------|------|
| schema_type | string | 是 | max_length=100 | Schema 类型 |
| content | string | 是 | min_length=1, max_length=1000000 | 内容文本 |
| url | string | 否 | max_length=2048 | 内容 URL |
| metadata | object | 否 | max_keys=50 | 额外元数据 |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/schema/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_type": "Article",
    "content": "This is a comprehensive guide to AI...",
    "url": "https://example.com/ai-guide",
    "metadata": {
      "author": "Jane Smith",
      "publish_date": "2025-10-26"
    }
  }'
```

**响应**：

```json
{
  "schema": {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "AI Guide",
    "author": {
      "@type": "Person",
      "name": "Jane Smith"
    },
    "datePublished": "2025-10-26",
    "url": "https://example.com/ai-guide"
  },
  "is_valid": true,
  "errors": [],
  "warnings": ["Missing recommended field: image"],
  "completeness_score": 87.5,
  "suggestions": ["Add an image to improve SEO visibility"]
}
```

**错误响应（422）**：

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "content"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

---

### 3.6 验证 Schema

#### POST /api/v1/schema/validate

**描述**：验证 Schema.org JSON-LD 的完整性

**查询参数**：

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|-------|------|
| structured | boolean | false | 是否返回结构化错误 |

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|-----|------|------|------|------|
| schema | object | 是 | max_keys=100 | 要验证的 Schema |

**请求示例（简单模式）**：

```bash
curl -X POST http://localhost:8000/api/v1/schema/validate \
  -H "Content-Type: application/json" \
  -d '{
    "schema": {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "My Article"
    }
  }'
```

**响应（简单模式）**：

```json
{
  "is_valid": false,
  "errors": [
    "Missing required field: datePublished",
    "Missing required field: author"
  ],
  "warnings": [
    "Missing recommended field: image"
  ],
  "completeness_score": 50.0,
  "suggestions": [
    "Add datePublished field to meet Schema.org requirements",
    "Add author field",
    "Add image for better search visibility"
  ]
}
```

**请求示例（结构化模式）**：

```bash
curl -X POST "http://localhost:8000/api/v1/schema/validate?structured=true" \
  -H "Content-Type: application/json" \
  -d '{
    "schema": {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "My Article"
    }
  }'
```

**响应（结构化模式）**：

```json
{
  "is_valid": false,
  "errors": [
    {
      "path": "/datePublished",
      "code": "MISSING_REQUIRED_FIELD",
      "message": "Missing required field: datePublished",
      "severity": "ERROR"
    },
    {
      "path": "/author",
      "code": "MISSING_REQUIRED_FIELD",
      "message": "Missing required field: author",
      "severity": "ERROR"
    }
  ],
  "warnings": [
    {
      "path": "/image",
      "code": "MISSING_RECOMMENDED_FIELD",
      "message": "Missing recommended field: image",
      "severity": "WARNING"
    }
  ],
  "completeness_score": 50.0,
  "suggestions": [
    "Add datePublished field to meet Schema.org requirements",
    "Add author field",
    "Add image for better search visibility"
  ]
}
```

---

### 3.7 WordPress 注入

#### POST /api/v1/wordpress/inject

**描述**：将 Schema 注入到 WordPress 文章/页面

**请求体**：

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| site_url | string | 是 | WordPress 站点 URL |
| username | string | 是 | WordPress 用户名 |
| app_password | string | 是 | Application Password |
| post_id | integer | 是 | 文章/页面 ID |
| schema | object | 是 | 要注入的 Schema |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/wordpress/inject \
  -H "Content-Type: application/json" \
  -d '{
    "site_url": "https://your-wordpress-site.com",
    "username": "admin",
    "app_password": "xxxx xxxx xxxx xxxx xxxx xxxx",
    "post_id": 123,
    "schema": {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "My Article",
      ...
    }
  }'
```

**响应（成功）**：

```json
{
  "success": true,
  "message": "Schema injected successfully",
  "post_id": 123,
  "post_url": "https://your-wordpress-site.com/my-article"
}
```

**响应（失败）**：

```json
{
  "success": false,
  "message": "Failed to inject schema: Authentication failed",
  "error_code": "WORDPRESS_AUTH_ERROR"
}
```

---

## 4. 数据模型

### 4.1 SchemaGenerateRequest

```typescript
{
  schema_type: string;      // max_length=100
  content: string;          // min_length=1, max_length=1000000
  url?: string;             // max_length=2048
  metadata?: {              // max_keys=50
    [key: string]: any;
  };
}
```

### 4.2 SchemaGenerateResponse

```typescript
{
  schema: object;           // 生成的 Schema.org JSON-LD
  is_valid: boolean;        // 是否有效
  errors: string[];         // 错误列表
  warnings: string[];       // 警告列表
  completeness_score: number;  // 完整度评分 (0-100)
  suggestions: string[];    // 优化建议
}
```

### 4.3 SchemaValidateRequest

```typescript
{
  schema: object;           // max_keys=100
}
```

### 4.4 SchemaValidateResponse（简单模式）

```typescript
{
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  completeness_score: number;
  suggestions: string[];
}
```

### 4.5 StructuredSchemaValidateResponse（结构化模式）

```typescript
{
  is_valid: boolean;
  errors: StructuredValidationError[];
  warnings: StructuredValidationError[];
  completeness_score: number;
  suggestions: string[];
}
```

### 4.6 StructuredValidationError

```typescript
{
  path: string;             // JSON Path (e.g., "/headline")
  code: string;             // Error code (e.g., "MISSING_REQUIRED_FIELD")
  message: string;          // Human-readable message
  severity: "ERROR" | "WARNING";
}
```

---

## 5. 错误码

### 5.1 验证错误码

| 错误码 | 说明 | 示例 |
|-------|------|------|
| MISSING_CONTEXT | 缺少 @context | `{"path": "/@context", "code": "MISSING_CONTEXT"}` |
| MISSING_TYPE | 缺少 @type | `{"path": "/@type", "code": "MISSING_TYPE"}` |
| MISSING_REQUIRED_FIELD | 缺少必填字段 | `{"path": "/headline", "code": "MISSING_REQUIRED_FIELD"}` |
| MISSING_RECOMMENDED_FIELD | 缺少推荐字段 | `{"path": "/image", "code": "MISSING_RECOMMENDED_FIELD"}` |
| INVALID_SCHEMA_TYPE | 无效的 Schema 类型 | `{"error_code": "INVALID_SCHEMA_TYPE"}` |

### 5.2 WordPress 错误码

| 错误码 | 说明 |
|-------|------|
| WORDPRESS_AUTH_ERROR | WordPress 认证失败 |
| WORDPRESS_POST_NOT_FOUND | 文章不存在 |
| WORDPRESS_INJECTION_ERROR | 注入失败 |

### 5.3 系统错误码

| 错误码 | 说明 |
|-------|------|
| INTERNAL_ERROR | 服务器内部错误 |
| VALIDATION_ERROR | 请求参数验证失败 |
| REQUEST_TOO_LARGE | 请求体过大 |

---

## 6. 代码示例

### 6.1 Python

```python
import requests

# 生成 Schema
response = requests.post(
    "http://localhost:8000/api/v1/schema/generate",
    json={
        "schema_type": "Article",
        "content": "This is a test article...",
        "url": "https://example.com/article",
        "metadata": {"author": "John Doe"}
    }
)

data = response.json()
print(f"Completeness Score: {data['completeness_score']}%")
print(f"Schema: {data['schema']}")

# 验证 Schema（结构化模式）
validate_response = requests.post(
    "http://localhost:8000/api/v1/schema/validate?structured=true",
    json={"schema": data["schema"]}
)

validation = validate_response.json()
for error in validation["errors"]:
    print(f"Error at {error['path']}: {error['message']}")
```

### 6.2 JavaScript (Node.js)

```javascript
const axios = require('axios');

async function generateSchema() {
  const response = await axios.post(
    'http://localhost:8000/api/v1/schema/generate',
    {
      schema_type: 'Product',
      content: 'Premium wireless headphones...',
      url: 'https://shop.example.com/headphones',
      metadata: {
        price: '299.99',
        currency: 'USD',
        brand: 'AudioTech'
      }
    }
  );

  console.log('Completeness Score:', response.data.completeness_score);
  console.log('Schema:', JSON.stringify(response.data.schema, null, 2));
}

generateSchema();
```

### 6.3 cURL

```bash
# 生成 Schema
curl -X POST http://localhost:8000/api/v1/schema/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "schema_type": "Recipe",
    "content": "Delicious chocolate cake...",
    "url": "https://recipes.example.com/chocolate-cake"
  }'

# 验证 Schema（结构化模式）
curl -X POST "http://localhost:8000/api/v1/schema/validate?structured=true" \
  -H "Content-Type: application/json" \
  -d '{
    "schema": {
      "@context": "https://schema.org",
      "@type": "Recipe",
      "name": "Chocolate Cake"
    }
  }'
```

### 6.4 PHP

```php
<?php

$data = [
    'schema_type' => 'Event',
    'content' => 'Join us for Tech Summit 2025...',
    'url' => 'https://events.example.com/tech-summit',
    'metadata' => [
        'start_date' => '2025-11-15T09:00:00',
        'location' => 'San Francisco'
    ]
];

$ch = curl_init('http://localhost:8000/api/v1/schema/generate');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-API-Key: your-secret-key'
]);

$response = curl_exec($ch);
curl_close($ch);

$result = json_decode($response, true);
echo "Completeness Score: " . $result['completeness_score'] . "%\n";
?>
```

---

## 4. 支持的 Schema 类型

### 4.1 类型列表

| Schema 类型 | 适用场景 | 必需字段 | 推荐字段 | 性能 (ops/sec) |
|------------|---------|---------|---------|----------------|
| **Article** | 博客、新闻 | headline, author | image, datePublished, publisher | 275,184 |
| **Product** | 电商、商城 | name | brand, offers, image, aggregateRating | 713,692 |
| **Recipe** | 美食网站 | name, recipeIngredient, recipeInstructions | image, prepTime, cookTime, nutrition | 232,284 |
| **Event** | 会议、演出 | name, startDate, location | image, offers, organizer | 117,508 |
| **Organization** | 公司官网 | name | url, logo, description, address | 346,021 |
| **Person** | 个人主页 | name | url, image, jobTitle | 236,407 |
| **FAQPage** | 客服页面 | mainEntity | description, name | 26,332 |
| **HowTo** | 操作指南 | name, step | image, description, totalTime | - |
| **Course** | 在线教育 | name, description, provider | url, offers, aggregateRating | - |

### 4.2 字段规范化

所有生成的 Schema 都会自动进行字段规范化：

| 字段类型 | 规范化规则 | 示例 |
|---------|-----------|------|
| **日期** | ISO8601 格式 | `2024-01-15T10:30:00Z` |
| **URL** | 绝对路径 | `https://example.com/article` |
| **货币** | ISO4217 代码 | `USD`, `EUR`, `CNY` |
| **语言** | BCP47 代码 | `en-US`, `zh-CN` |
| **嵌套对象** | 带 `@type` 标记 | `{"@type": "Person", "name": "..."}` |

---

## 8. 性能指标

### 8.1 实际 Benchmark 测试结果

基于 **pytest-benchmark** 的真实测试数据（569 个测试，100% 通过）：

| 操作 | 平均耗时 | 吞吐量 (ops/sec) | 评价 |
|------|---------|-----------------|------|
| **Article 生成** | 3.63 μs | 275,184 | ⚡ 优秀 |
| **Product 生成** | 1.40 μs | 713,692 | ⚡ 优秀 |
| **Article 验证** | 3.46 μs | 289,190 | ⚡ 优秀 |
| **批量生成 (10个)** | 243 μs | 4,114 | ✅ 良好 |

### 8.2 API 响应时间

| 端点 | P50 | P95 | P99 |
|-----|-----|-----|-----|
| `/api/v1/schema/generate` | < 5ms | < 20ms | < 50ms |
| `/api/v1/schema/validate` | < 3ms | < 15ms | < 30ms |
| `/api/v1/schema/types` | < 1ms | < 2ms | < 5ms |
| `/api/v1/schema/template` | < 1ms | < 2ms | < 5ms |

### 8.3 并发性能

| 并发数 | 响应时间 | 成功率 |
|--------|---------|--------|
| 1 | < 10 μs | 100% |
| 10 | < 50 μs | 100% |
| 100 | < 500 μs | 100% |
| 1000 | < 5 ms | 100% |

**结论**：微秒级响应时间，可轻松支持高并发场景。

---

**文档版本**：1.0.0
**测试覆盖率**：97% (569/569 tests)
**生产状态**：✅ Production Ready
**最后更新**：2025-10-27

