# P0-2: Validator 结构化错误输出设计文档

**版本**: 1.0  
**日期**: 2025-10-21  
**状态**: 设计阶段

---

## 一、设计目标

将 SchemaValidator 的错误输出从简单字符串列表升级为结构化对象，支持：

1. **字段路径追踪** - 使用 JSON Pointer (RFC 6901) 定位错误字段
2. **错误码系统** - 机器可读的错误分类
3. **可本地化消息** - 支持多语言错误提示
4. **严重级分类** - ERROR（阻塞）vs WARNING（建议）
5. **嵌套对象深度验证** - 验证 Offer/Address/Rating 等子对象

---

## 二、错误对象结构

### 2.1 ValidationError 数据结构

```python
{
    "path": str,           # JSON Pointer 路径，如 "/offers/price"
    "code": str,           # 错误码，如 "MISSING_REQUIRED_FIELD"
    "message": str,        # 人类可读消息（英文）
    "message_key": str,    # i18n 消息键，如 "error.missing_required_field"
    "severity": str,       # "ERROR" | "WARNING"
    "context": dict        # 额外上下文信息（可选）
}
```

### 2.2 ValidationResult 数据结构

```python
{
    "is_valid": bool,                    # 是否通过验证（无 ERROR）
    "errors": List[ValidationError],     # 错误列表（severity=ERROR）
    "warnings": List[ValidationError],   # 警告列表（severity=WARNING）
    "completeness_score": float,         # 完整度评分 0-100
    "suggestions": List[str]             # 优化建议（保持向后兼容）
}
```

---

## 三、JSON Pointer 路径规范

遵循 RFC 6901 标准：

| 字段位置 | JSON Pointer 路径 | 示例 |
|---------|------------------|------|
| 根字段 | `/@type` | `"/@type"` |
| 嵌套对象字段 | `/offers/price` | `"/offers/price"` |
| 数组元素 | `/image/0/url` | `"/image/0/url"` |
| 深层嵌套 | `/location/address/streetAddress` | `"/location/address/streetAddress"` |

**特殊情况**:
- 根级错误（如缺少 @context）：路径为 `""`（空字符串）
- 整个对象错误：路径为 `"/"`

---

## 四、错误码分类系统

### 4.1 结构性错误 (STRUCTURAL_*)

| 错误码 | 描述 | 示例 |
|-------|------|------|
| `MISSING_CONTEXT` | 缺少 @context | `{"path": "", "code": "MISSING_CONTEXT"}` |
| `MISSING_TYPE` | 缺少 @type | `{"path": "", "code": "MISSING_TYPE"}` |
| `INVALID_CONTEXT` | @context 值不正确 | `{"path": "/@context", "code": "INVALID_CONTEXT"}` |

### 4.2 必填字段错误 (REQUIRED_*)

| 错误码 | 描述 | 示例 |
|-------|------|------|
| `MISSING_REQUIRED_FIELD` | 缺少必填字段 | `{"path": "/headline", "code": "MISSING_REQUIRED_FIELD"}` |
| `EMPTY_REQUIRED_FIELD` | 必填字段为空 | `{"path": "/name", "code": "EMPTY_REQUIRED_FIELD"}` |

### 4.3 类型错误 (TYPE_*)

| 错误码 | 描述 | 示例 |
|-------|------|------|
| `INVALID_TYPE` | 字段类型不正确 | `{"path": "/author/@type", "code": "INVALID_TYPE", "context": {"expected": "Person", "actual": "Organization"}}` |
| `INVALID_VALUE_TYPE` | 值类型不匹配 | `{"path": "/datePublished", "code": "INVALID_VALUE_TYPE", "context": {"expected": "string", "actual": "number"}}` |
| `INVALID_ARRAY_ITEM` | 数组元素类型错误 | `{"path": "/recipeIngredient/2", "code": "INVALID_ARRAY_ITEM"}` |

### 4.4 嵌套对象错误 (NESTED_*)

| 错误码 | 描述 | 示例 |
|-------|------|------|
| `NESTED_MISSING_TYPE` | 嵌套对象缺少 @type | `{"path": "/offers/@type", "code": "NESTED_MISSING_TYPE"}` |
| `NESTED_MISSING_FIELD` | 嵌套对象缺少必填字段 | `{"path": "/offers/price", "code": "NESTED_MISSING_FIELD"}` |
| `NESTED_INVALID_TYPE` | 嵌套对象类型错误 | `{"path": "/location/@type", "code": "NESTED_INVALID_TYPE", "context": {"expected": "Place", "actual": "Organization"}}` |

### 4.5 格式错误 (FORMAT_*)

| 错误码 | 描述 | 示例 |
|-------|------|------|
| `INVALID_DATE_FORMAT` | 日期格式不正确 | `{"path": "/datePublished", "code": "INVALID_DATE_FORMAT"}` |
| `INVALID_URL_FORMAT` | URL 格式不正确 | `{"path": "/url", "code": "INVALID_URL_FORMAT"}` |
| `INVALID_CURRENCY_CODE` | 货币代码不正确 | `{"path": "/offers/priceCurrency", "code": "INVALID_CURRENCY_CODE"}` |

### 4.6 推荐字段警告 (RECOMMENDED_*)

| 错误码 | 描述 | 示例 |
|-------|------|------|
| `MISSING_RECOMMENDED_FIELD` | 缺少推荐字段 | `{"path": "/image", "code": "MISSING_RECOMMENDED_FIELD", "severity": "WARNING"}` |
| `INCOMPLETE_NESTED_OBJECT` | 嵌套对象不完整 | `{"path": "/offers/availability", "code": "INCOMPLETE_NESTED_OBJECT", "severity": "WARNING"}` |

---

## 五、嵌套对象验证规则

### 5.1 Offer 对象

**必填字段**: `@type`, `price` 或 `priceSpecification`  
**推荐字段**: `priceCurrency`, `availability`, `url`

```python
# 验证规则
if offers["@type"] != "Offer":
    errors.append({
        "path": "/offers/@type",
        "code": "NESTED_INVALID_TYPE",
        "message": "offers must be of type Offer",
        "message_key": "error.nested_invalid_type",
        "severity": "ERROR",
        "context": {"expected": "Offer", "actual": offers.get("@type")}
    })

if "price" not in offers and "priceSpecification" not in offers:
    errors.append({
        "path": "/offers/price",
        "code": "NESTED_MISSING_FIELD",
        "message": "offers must have price or priceSpecification",
        "message_key": "error.nested_missing_field",
        "severity": "ERROR"
    })

if "priceCurrency" not in offers:
    warnings.append({
        "path": "/offers/priceCurrency",
        "code": "MISSING_RECOMMENDED_FIELD",
        "message": "Add priceCurrency for proper price display",
        "message_key": "warning.missing_recommended_field",
        "severity": "WARNING"
    })
```

### 5.2 PostalAddress 对象

**必填字段**: `@type`  
**推荐字段**: `streetAddress`, `addressLocality`, `addressRegion`, `postalCode`, `addressCountry`

```python
# 验证规则
if address.get("@type") != "PostalAddress":
    errors.append({
        "path": f"{parent_path}/address/@type",
        "code": "NESTED_INVALID_TYPE",
        "message": "address must be of type PostalAddress",
        "message_key": "error.nested_invalid_type",
        "severity": "ERROR",
        "context": {"expected": "PostalAddress", "actual": address.get("@type")}
    })

# 推荐字段检查
recommended = ["streetAddress", "addressLocality", "postalCode"]
for field in recommended:
    if field not in address:
        warnings.append({
            "path": f"{parent_path}/address/{field}",
            "code": "MISSING_RECOMMENDED_FIELD",
            "message": f"Add {field} for complete address",
            "message_key": "warning.missing_recommended_field",
            "severity": "WARNING"
        })
```

### 5.3 AggregateRating 对象

**必填字段**: `@type`, `ratingValue`, `reviewCount`  
**推荐字段**: `bestRating`, `worstRating`

```python
# 验证规则
required = ["@type", "ratingValue", "reviewCount"]
for field in required:
    if field not in rating:
        errors.append({
            "path": f"{parent_path}/aggregateRating/{field}",
            "code": "NESTED_MISSING_FIELD",
            "message": f"aggregateRating must have {field}",
            "message_key": "error.nested_missing_field",
            "severity": "ERROR"
        })

# 值范围检查
if "ratingValue" in rating:
    value = rating["ratingValue"]
    if not isinstance(value, (int, float)) or value < 0:
        errors.append({
            "path": f"{parent_path}/aggregateRating/ratingValue",
            "code": "INVALID_VALUE_TYPE",
            "message": "ratingValue must be a positive number",
            "message_key": "error.invalid_value_type",
            "severity": "ERROR"
        })
```

### 5.4 ImageObject 对象

**必填字段**: `@type`, `url`  
**推荐字段**: `width`, `height`, `caption`

```python
# 验证规则
if isinstance(image, dict):
    if image.get("@type") != "ImageObject":
        errors.append({
            "path": f"{parent_path}/image/@type",
            "code": "NESTED_INVALID_TYPE",
            "message": "image must be of type ImageObject",
            "message_key": "error.nested_invalid_type",
            "severity": "ERROR"
        })
    
    if "url" not in image:
        errors.append({
            "path": f"{parent_path}/image/url",
            "code": "NESTED_MISSING_FIELD",
            "message": "ImageObject must have url",
            "message_key": "error.nested_missing_field",
            "severity": "ERROR"
        })
```

### 5.5 HowToStep 对象

**必填字段**: `@type`, `text`  
**推荐字段**: `name`, `url`, `image`

```python
# 验证规则（数组元素）
for i, step in enumerate(steps):
    if not isinstance(step, dict):
        errors.append({
            "path": f"{parent_path}/recipeInstructions/{i}",
            "code": "INVALID_ARRAY_ITEM",
            "message": f"Step {i} must be a HowToStep object",
            "message_key": "error.invalid_array_item",
            "severity": "ERROR"
        })
        continue
    
    if step.get("@type") != "HowToStep":
        errors.append({
            "path": f"{parent_path}/recipeInstructions/{i}/@type",
            "code": "NESTED_INVALID_TYPE",
            "message": f"Step {i} must be of type HowToStep",
            "message_key": "error.nested_invalid_type",
            "severity": "ERROR"
        })
    
    if "text" not in step:
        errors.append({
            "path": f"{parent_path}/recipeInstructions/{i}/text",
            "code": "NESTED_MISSING_FIELD",
            "message": f"Step {i} must have text",
            "message_key": "error.nested_missing_field",
            "severity": "ERROR"
        })
```

### 5.6 NutritionInformation 对象

**必填字段**: `@type`  
**推荐字段**: `calories`, `fatContent`, `proteinContent`, `carbohydrateContent`

```python
# 验证规则
if nutrition.get("@type") != "NutritionInformation":
    errors.append({
        "path": f"{parent_path}/nutrition/@type",
        "code": "NESTED_INVALID_TYPE",
        "message": "nutrition must be of type NutritionInformation",
        "message_key": "error.nested_invalid_type",
        "severity": "ERROR"
    })

# 推荐字段
recommended = ["calories", "fatContent", "proteinContent"]
for field in recommended:
    if field not in nutrition:
        warnings.append({
            "path": f"{parent_path}/nutrition/{field}",
            "code": "MISSING_RECOMMENDED_FIELD",
            "message": f"Add {field} for nutritional information",
            "message_key": "warning.missing_recommended_field",
            "severity": "WARNING"
        })
```

---

## 六、i18n 消息键映射

```python
MESSAGE_KEYS = {
    # 结构性错误
    "MISSING_CONTEXT": "error.missing_context",
    "MISSING_TYPE": "error.missing_type",
    "INVALID_CONTEXT": "error.invalid_context",
    
    # 必填字段错误
    "MISSING_REQUIRED_FIELD": "error.missing_required_field",
    "EMPTY_REQUIRED_FIELD": "error.empty_required_field",
    
    # 类型错误
    "INVALID_TYPE": "error.invalid_type",
    "INVALID_VALUE_TYPE": "error.invalid_value_type",
    "INVALID_ARRAY_ITEM": "error.invalid_array_item",
    
    # 嵌套对象错误
    "NESTED_MISSING_TYPE": "error.nested_missing_type",
    "NESTED_MISSING_FIELD": "error.nested_missing_field",
    "NESTED_INVALID_TYPE": "error.nested_invalid_type",
    
    # 格式错误
    "INVALID_DATE_FORMAT": "error.invalid_date_format",
    "INVALID_URL_FORMAT": "error.invalid_url_format",
    "INVALID_CURRENCY_CODE": "error.invalid_currency_code",
    
    # 推荐字段警告
    "MISSING_RECOMMENDED_FIELD": "warning.missing_recommended_field",
    "INCOMPLETE_NESTED_OBJECT": "warning.incomplete_nested_object"
}
```

---

## 七、向后兼容性

为保持向后兼容，SchemaValidator 将提供两种模式：

### 7.1 新模式（结构化错误）

```python
validator = SchemaValidator(structured_errors=True)
result = validator.validate(schema)

# 返回:
{
    "is_valid": False,
    "errors": [
        {
            "path": "/offers/price",
            "code": "NESTED_MISSING_FIELD",
            "message": "offers must have price or priceSpecification",
            "message_key": "error.nested_missing_field",
            "severity": "ERROR"
        }
    ],
    "warnings": [...],
    "completeness_score": 75.0,
    "suggestions": [...]
}
```

### 7.2 旧模式（字符串列表，默认）

```python
validator = SchemaValidator()  # structured_errors=False (默认)
is_valid, errors, warnings = validator.validate(schema)

# 返回:
# is_valid = False
# errors = ["offers must have price or priceSpecification"]
# warnings = ["Missing recommended fields: image, brand"]
```

---

## 八、实现计划

1. **P0-2.1** ✅ 设计文档（本文档）
2. **P0-2.2** 实现嵌套对象验证规则
   - 创建 `_validate_nested_offer()`
   - 创建 `_validate_nested_address()`
   - 创建 `_validate_nested_rating()`
   - 创建 `_validate_nested_image()`
   - 创建 `_validate_nested_howto_step()`
   - 创建 `_validate_nested_nutrition()`
3. **P0-2.3** 更新 SchemaValidator 返回结构
   - 修改 `validate()` 方法支持结构化错误
   - 更新 API 响应模型（Pydantic）
4. **P0-2.4** 添加单元测试
   - 测试所有嵌套对象验证规则
   - 测试字段路径生成
   - 测试错误码分类
5. **P0-2.5** 更新文档与验收
   - 创建完成报告
   - 更新 API 文档
   - 提供验收步骤

---

**设计完成** | 下一步：实现嵌套对象验证规则 (P0-2.2)

