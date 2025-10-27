# API 文档

## Schema 生成

### POST /api/v1/schema/generate

生成指定类型的 Schema.org 结构化数据。

**请求体**:
```json
{
  "schema_type": "Article",
  "content": "文章内容...",
  "url": "https://example.com/article",  // 可选
  "metadata": {                           // 可选
    "author": "作者名",
    "date": "2025-10-21",
    "publisher_name": "发布者",
    "publisher_logo": "https://example.com/logo.png"
  }
}
```

**响应**:
```json
{
  "schema": {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "...",
    "author": {...},
    "publisher": {...}
  },
  "completeness_score": 85.5,
  "warnings": [
    "Missing recommended field: image"
  ]
}
```

---

## Schema 验证

### POST /api/v1/schema/validate

验证 Schema.org 结构化数据的有效性和完整性。

**请求体**:
```json
{
  "schema": {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "产品名称",
    "offers": {
      "@type": "Offer",
      "price": "99.99",
      "priceCurrency": "USD"
    }
  }
}
```

**响应（默认格式）**:
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [
    "Missing recommended field: image",
    "Missing recommended field: description"
  ],
  "completeness_score": 75.0,
  "suggestions": [
    "Add 'image' field for better SEO",
    "Add 'description' field for better SEO"
  ]
}
```

**错误响应示例**:
```json
{
  "is_valid": false,
  "errors": [
    "Missing required field: author",
    "Offer must have 'price' or 'priceSpecification'"
  ],
  "warnings": [...],
  "completeness_score": 45.0,
  "suggestions": [...]
}
```

### 结构化错误输出（高级）

验证器支持结构化错误输出，提供更详细的错误信息，包括字段路径、错误码和国际化消息键。

**注意**: 此功能目前仅在后端服务层可用，API 端点暂未暴露。如需使用，请直接调用 `SchemaValidator(structured_errors=True)`。

**结构化错误格式**:
```json
{
  "is_valid": false,
  "errors": [
    {
      "path": "/offers/price",
      "code": "NESTED_MISSING_REQUIRED_FIELD",
      "message": "Offer must have 'price' or 'priceSpecification'",
      "message_key": "error.nested_missing_required_field",
      "severity": "ERROR",
      "context": {}
    }
  ],
  "warnings": [
    {
      "path": "/image",
      "code": "MISSING_RECOMMENDED_FIELD",
      "message": "Missing recommended field: image",
      "message_key": "warning.missing_recommended_field",
      "severity": "WARNING",
      "context": {}
    }
  ],
  "completeness_score": 65.5,
  "suggestions": ["Add 'image' field for better SEO"]
}
```

**错误码分类**:

| 类别 | 错误码 | 说明 |
|------|--------|------|
| 结构性错误 | `MISSING_CONTEXT`, `MISSING_TYPE` | Schema 基础结构问题 |
| 必填字段 | `MISSING_REQUIRED_FIELD` | 必填字段缺失 |
| 类型错误 | `INVALID_TYPE` | 字段类型不匹配 |
| 嵌套对象 | `NESTED_INVALID_TYPE`, `NESTED_MISSING_REQUIRED_FIELD` | 嵌套对象验证失败 |
| 格式错误 | `INVALID_URL`, `INVALID_DATE` | 字段格式不正确 |
| 推荐字段 | `MISSING_RECOMMENDED_FIELD` | 推荐字段缺失（警告） |

**字段路径（JSON Pointer）**:

路径遵循 RFC 6901 JSON Pointer 规范：

- `/author` - 根级字段
- `/offers/price` - 嵌套对象字段
- `/image/0/url` - 数组第 1 项的字段
- `/publisher/logo/url` - 深层嵌套字段

---

## 查询支持的类型

### GET /api/v1/schema/types

获取所有支持的 Schema 类型列表。

**响应**:
```json
{
  "types": [
    "Article",
    "Product",
    "Organization",
    "Event",
    "Person",
    "Recipe",
    "FAQPage",
    "HowTo",
    "Course"
  ]
}
```

---

## 获取模板

### GET /api/v1/schema/template/{schema_type}

获取指定类型的 Schema 模板，包含必填和可选字段列表。

**路径参数**:
- `schema_type`: Schema 类型（如 "Article", "Product" 等）

**响应**:
```json
{
  "type": "Article",
  "required": ["headline", "author"],
  "optional": [
    "description",
    "image",
    "publisher",
    "dateModified",
    "articleBody",
    "datePublished"
  ]
}
```

---

## 支持的 Schema 类型

| 类型 | 必填字段 | 推荐字段 | 嵌套对象支持 |
|------|---------|---------|-------------|
| **Article** | headline, author | image, publisher, datePublished, description | Organization, Person, ImageObject |
| **Product** | name | offers, description, image, brand, aggregateRating | Offer, Brand, AggregateRating, ImageObject |
| **Recipe** | name, recipeIngredient, recipeInstructions | image, author, nutrition, prepTime, cookTime | Person, NutritionInformation, HowToStep, ImageObject |
| **Event** | name, startDate, location | description, organizer, performer, endDate | Place, Organization, Person, PostalAddress |
| **Organization** | name | url, logo, address, contactPoint | PostalAddress, ImageObject, ContactPoint |
| **Person** | name | url, jobTitle, worksFor, address | Organization, PostalAddress |
| **FAQPage** | mainEntity | - | Question, Answer |
| **HowTo** | name, step | description, image, totalTime | HowToStep, ImageObject |
| **Course** | name, description, provider | - | Organization |

---

## 嵌套对象验证

验证器对以下嵌套对象类型进行深度验证：

### Offer
- **必需**: `@type` (必须为 "Offer"), `price` 或 `priceSpecification`
- **推荐**: `priceCurrency`, `availability`

### AggregateRating
- **必需**: `@type` (必须为 "AggregateRating"), `ratingValue` (数字), `reviewCount`
- **推荐**: `bestRating`, `worstRating`

### PostalAddress
- **必需**: `@type` (必须为 "PostalAddress")
- **推荐**: `streetAddress`, `addressLocality`, `postalCode`, `addressCountry`
- **注意**: 也接受字符串格式的地址

### ImageObject
- **必需**: `@type` (必须为 "ImageObject"), `url`
- **推荐**: `width`, `height`
- **注意**: 也接受字符串 URL 或 ImageObject 数组

### HowToStep
- **必需**: `@type` (必须为 "HowToStep"), `text`
- **推荐**: `name`, `url`, `image`

### NutritionInformation
- **必需**: `@type` (必须为 "NutritionInformation")
- **推荐**: `calories`, `fatContent`, `proteinContent`, `carbohydrateContent`

### Organization
- **必需**: `@type` (必须为 "Organization"), `name`
- **推荐**: `url`, `logo` (ImageObject)

---

## 字段规范化

生成器自动对以下字段进行规范化：

### 日期/时间
- **格式**: ISO 8601 (YYYY-MM-DD 或 YYYY-MM-DDTHH:MM:SS)
- **支持输入**: datetime 对象, 字符串 (多种格式)

### URL
- **格式**: 绝对 URL
- **转换**: 相对路径 → 绝对 URL (基于提供的 base_url)

### 货币
- **格式**: ISO 4217 货币代码 (USD, EUR, GBP, CNY 等)
- **默认**: USD (如果无法识别)

### 语言
- **格式**: BCP 47 语言标签 (en-US, zh-CN 等)
- **支持**: 常见语言代码

---

## 站点级默认配置

生成器支持站点级默认配置，避免重复传递相同的元数据：

```python
from backend.services.schema_generator import SchemaGenerator

generator = SchemaGenerator(site_defaults={
    "publisher_name": "我的网站",
    "publisher_logo": "https://example.com/logo.png",
    "brand_name": "我的品牌",
    "brand_logo": "https://example.com/brand-logo.png"
})

# 生成 Article 时自动使用 publisher_name 和 publisher_logo
schema = generator.generate("Article", "文章内容...")
```

**优先级**: 方法参数 > site_defaults > 内置默认值

---

## 错误处理

所有 API 端点在发生错误时返回标准错误响应：

```json
{
  "detail": "错误描述信息"
}
```

**常见错误**:

| HTTP 状态码 | 错误 | 说明 |
|------------|------|------|
| 400 | Bad Request | 请求参数无效 |
| 404 | Not Found | Schema 类型不存在 |
| 422 | Unprocessable Entity | 请求体格式错误 |
| 500 | Internal Server Error | 服务器内部错误 |
