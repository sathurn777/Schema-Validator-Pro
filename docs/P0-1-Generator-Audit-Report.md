# P0-1: Schema Generator 审计报告与改进方案

**日期**: 2025-10-21  
**目标**: 将 Schema Generator 提升至"极致"标准  
**验收标准**: 
- 9 类模板推荐字段覆盖率 ≥80%
- 嵌套对象严格符合 schema.org 规范（带 @type）
- 字段规范化（ISO8601 日期、绝对 URL、ISO4217 货币、BCP47 语言）
- 支持站点级默认配置（publisher/logo/brand）

---

## 一、审计发现总结

### 1.1 当前实现优势
✅ 支持 9 种核心类型（Article/Product/Organization/Event/Person/Recipe/FAQPage/HowTo/Course）  
✅ 模板式生成，结构清晰  
✅ 基础字段提取逻辑可用  
✅ 已有 36 个单元测试全部通过  

### 1.2 关键差距（阻碍"极致"）

#### **嵌套对象结构不完整**
| 类型 | 当前问题 | schema.org 要求 |
|------|---------|----------------|
| **Article** | `publisher` 为简单字符串 | 应为 `Organization` 类型，含 `name`/`logo` |
| **Article** | `image` 为简单 URL | 应为 `ImageObject` 或 URL 数组 |
| **Product** | `offers` 直接传递 | 应为 `Offer` 类型，含 `price`/`priceCurrency`/`availability` |
| **Product** | `aggregateRating` 直接传递 | 应为 `AggregateRating` 类型，含 `ratingValue`/`reviewCount` |
| **Product** | `brand` 为简单字符串 | 应为 `Brand` 或 `Organization` 类型 |
| **Event** | `location.address` 结构简化 | 应为完整 `PostalAddress` 类型 |
| **Recipe** | `recipeInstructions` 为文本 | 应为 `HowToStep` 数组，每步含 `text`/`name`/`url` |
| **Recipe** | 缺少 `nutrition` | 应为 `NutritionInformation` 类型 |
| **Organization** | `address` 为简单字符串 | 应为 `PostalAddress` 类型 |
| **Person** | `address` 为简单字符串 | 应为 `PostalAddress` 类型 |

#### **推荐字段覆盖不足**
| 类型 | 当前覆盖 | 缺失关键字段 |
|------|---------|-------------|
| **Article** | ~50% | `publisher` (Organization)、`mainEntityOfPage`、`wordCount` |
| **Product** | ~40% | `brand` (Brand)、`sku`、`gtin13`、`manufacturer` |
| **Recipe** | ~60% | `nutrition`、`recipeCategory`、`recipeCuisine`、`cookingMethod` |
| **Event** | ~55% | `organizer` (Organization/Person)、`performer`、`eventStatus` |
| **Organization** | ~50% | `contactPoint`、`sameAs`、`foundingDate` |

#### **字段规范化缺失**
- ❌ **日期**: 使用 `datetime.now().strftime("%Y-%m-%d")`，未验证 ISO8601 格式
- ❌ **URL**: 未验证绝对 URL，未处理相对路径
- ❌ **货币**: `priceCurrency` 未验证 ISO4217 代码（如 USD/EUR/CNY）
- ❌ **语言**: `inLanguage` 未验证 BCP47 标签（如 en-US/zh-CN）

#### **站点级默认配置缺失**
- ❌ 每次生成都需重新指定 `publisher`/`logo`/`brand`
- ❌ 无法为整个站点设置统一的 `sameAs`（社交媒体链接）
- ❌ 无法设置默认 `inLanguage`

---

## 二、改进方案

### 2.1 嵌套对象结构化（优先级 P0）

#### **Article 改进**
```python
# 当前（错误）
schema["publisher"] = kwargs.get("publisher", "Unknown Publisher")

# 改进后（正确）
schema["publisher"] = {
    "@type": "Organization",
    "name": kwargs.get("publisher_name", site_defaults.get("publisher_name", "Unknown Publisher")),
    "logo": {
        "@type": "ImageObject",
        "url": kwargs.get("publisher_logo", site_defaults.get("publisher_logo"))
    } if kwargs.get("publisher_logo") or site_defaults.get("publisher_logo") else None
}

# image 改进
if "image" in kwargs:
    images = kwargs["image"] if isinstance(kwargs["image"], list) else [kwargs["image"]]
    schema["image"] = [
        {"@type": "ImageObject", "url": self._normalize_url(img)} if isinstance(img, str) else img
        for img in images
    ]
```

#### **Product 改进**
```python
# offers 结构化
if "offers" in kwargs:
    schema["offers"] = {
        "@type": "Offer",
        "price": kwargs["offers"].get("price"),
        "priceCurrency": self._normalize_currency(kwargs["offers"].get("priceCurrency", "USD")),
        "availability": kwargs["offers"].get("availability", "https://schema.org/InStock"),
        "url": self._normalize_url(kwargs["offers"].get("url", url))
    }

# aggregateRating 结构化
if "aggregateRating" in kwargs:
    schema["aggregateRating"] = {
        "@type": "AggregateRating",
        "ratingValue": kwargs["aggregateRating"].get("ratingValue"),
        "reviewCount": kwargs["aggregateRating"].get("reviewCount"),
        "bestRating": kwargs["aggregateRating"].get("bestRating", 5),
        "worstRating": kwargs["aggregateRating"].get("worstRating", 1)
    }

# brand 结构化
if "brand" in kwargs:
    schema["brand"] = {
        "@type": "Brand",
        "name": kwargs["brand"] if isinstance(kwargs["brand"], str) else kwargs["brand"].get("name")
    }
```

#### **Recipe 改进**
```python
# recipeInstructions 结构化为 HowToStep 数组
if "recipeInstructions" in kwargs:
    instructions = kwargs["recipeInstructions"]
    if isinstance(instructions, str):
        # 按行拆分为步骤
        steps = [s.strip() for s in instructions.split("\n") if s.strip()]
        schema["recipeInstructions"] = [
            {
                "@type": "HowToStep",
                "text": step,
                "name": f"Step {i+1}",
                "position": i+1
            }
            for i, step in enumerate(steps)
        ]
    elif isinstance(instructions, list):
        schema["recipeInstructions"] = [
            {
                "@type": "HowToStep",
                "text": step if isinstance(step, str) else step.get("text"),
                "name": step.get("name", f"Step {i+1}") if isinstance(step, dict) else f"Step {i+1}",
                "position": i+1
            }
            for i, step in enumerate(instructions)
        ]

# nutrition 结构化
if "nutrition" in kwargs:
    schema["nutrition"] = {
        "@type": "NutritionInformation",
        "calories": kwargs["nutrition"].get("calories"),
        "fatContent": kwargs["nutrition"].get("fatContent"),
        "proteinContent": kwargs["nutrition"].get("proteinContent"),
        "carbohydrateContent": kwargs["nutrition"].get("carbohydrateContent")
    }
```

### 2.2 字段规范化器（优先级 P0）

```python
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re

class SchemaGenerator:
    # ISO4217 货币代码白名单（常用）
    VALID_CURRENCIES = {
        "USD", "EUR", "GBP", "JPY", "CNY", "AUD", "CAD", "CHF", "HKD", "SGD",
        "SEK", "NOK", "DKK", "NZD", "KRW", "INR", "BRL", "RUB", "ZAR", "MXN"
    }
    
    # BCP47 语言标签白名单（常用）
    VALID_LANGUAGES = {
        "en", "en-US", "en-GB", "zh", "zh-CN", "zh-TW", "ja", "ko", "fr", "de",
        "es", "it", "pt", "ru", "ar", "hi", "th", "vi", "id", "ms"
    }
    
    def _normalize_date(self, value: Any, format: str = "iso8601") -> str:
        """规范化日期为 ISO8601 格式"""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, str):
            # 尝试解析常见格式
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.date().isoformat()
                except ValueError:
                    continue
            # 如果已是 ISO8601 格式，直接返回
            if re.match(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?", value):
                return value
        return datetime.now().date().isoformat()
    
    def _normalize_url(self, value: str, base_url: Optional[str] = None) -> str:
        """规范化 URL 为绝对路径"""
        if not value:
            return value
        
        # 如果已是绝对 URL，直接返回
        parsed = urlparse(value)
        if parsed.scheme in ("http", "https"):
            return value
        
        # 如果是相对路径且提供了 base_url，拼接
        if base_url:
            return urljoin(base_url, value)
        
        # 否则返回原值（警告：可能不是有效 URL）
        return value
    
    def _normalize_currency(self, value: str) -> str:
        """验证并规范化 ISO4217 货币代码"""
        if not value:
            return "USD"  # 默认美元
        
        value_upper = value.upper()
        if value_upper in self.VALID_CURRENCIES:
            return value_upper
        
        # 如果不在白名单，返回默认值并记录警告
        return "USD"
    
    def _normalize_language(self, value: str) -> str:
        """验证并规范化 BCP47 语言标签"""
        if not value:
            return "en"  # 默认英语
        
        value_lower = value.lower()
        if value_lower in self.VALID_LANGUAGES:
            return value_lower
        
        # 尝试匹配主语言代码（如 zh-Hans-CN -> zh）
        main_lang = value_lower.split("-")[0]
        if main_lang in self.VALID_LANGUAGES:
            return main_lang
        
        return "en"
```

### 2.3 站点级默认配置（优先级 P0）

```python
class SchemaGenerator:
    def __init__(self, site_defaults: Optional[Dict[str, Any]] = None):
        """
        初始化生成器，支持站点级默认配置
        
        Args:
            site_defaults: 站点级默认元数据，例如：
                {
                    "publisher_name": "My News Site",
                    "publisher_logo": "https://example.com/logo.png",
                    "brand_name": "My Brand",
                    "sameAs": ["https://twitter.com/mysite", "https://facebook.com/mysite"],
                    "inLanguage": "en-US"
                }
        """
        self.site_defaults = site_defaults or {}
    
    def _get_default(self, key: str, kwargs: Dict[str, Any], fallback: Any = None) -> Any:
        """
        获取配置值，优先级：kwargs > site_defaults > fallback
        """
        return kwargs.get(key, self.site_defaults.get(key, fallback))
```

---

## 三、实施计划

### 阶段 1: 嵌套对象结构化（2-3 小时）
1. ✅ 创建审计报告（当前文件）
2. ⏳ 修改 `schema_generator.py`：
   - 为 Article/Product/Recipe/Event/Organization/Person 添加嵌套对象结构
   - 更新 SCHEMA_TEMPLATES 的 required/optional 字段列表
3. ⏳ 更新现有单元测试，确保不破坏兼容性

### 阶段 2: 字段规范化器（1-2 小时）
1. ⏳ 实现 4 个规范化方法（date/URL/currency/language）
2. ⏳ 在所有生成器方法中集成规范化器
3. ⏳ 添加规范化器单元测试

### 阶段 3: 站点级默认配置（1 小时）
1. ⏳ 修改 `__init__` 支持 `site_defaults` 参数
2. ⏳ 更新所有生成器方法使用 `_get_default`
3. ⏳ 添加站点默认配置测试

### 阶段 4: 文档与示例（1 小时）
1. ⏳ 更新 `docs/功能说明.md` 添加嵌套对象示例
2. ⏳ 创建 `docs/生成器配置指南.md` 说明站点默认配置
3. ⏳ 添加 Google Rich Results 测试示例

---

## 四、验收标准

### 4.1 嵌套对象验收
- [ ] Article.publisher 为 Organization 类型（含 name/logo）
- [ ] Product.offers 为 Offer 类型（含 price/priceCurrency/availability）
- [ ] Product.aggregateRating 为 AggregateRating 类型
- [ ] Recipe.recipeInstructions 为 HowToStep 数组
- [ ] Event.location.address 为 PostalAddress 类型

### 4.2 字段规范化验收
- [ ] 所有日期字段符合 ISO8601 格式
- [ ] 所有 URL 字段为绝对路径
- [ ] 所有 priceCurrency 为有效 ISO4217 代码
- [ ] 所有 inLanguage 为有效 BCP47 标签

### 4.3 站点默认配置验收
- [ ] 可通过 `site_defaults` 设置全局 publisher/logo/brand
- [ ] kwargs 优先级高于 site_defaults
- [ ] 未提供配置时使用合理默认值

### 4.4 测试覆盖验收
- [ ] 所有 36 个现有测试仍通过
- [ ] 新增 ≥15 个测试覆盖嵌套对象
- [ ] 新增 ≥8 个测试覆盖规范化器
- [ ] 新增 ≥5 个测试覆盖站点默认配置
- [ ] 总测试覆盖率 ≥90%

---

## 五、下一步行动

**立即开始**: 阶段 1 - 嵌套对象结构化  
**预计完成时间**: 2-3 小时  
**输出**: 
1. 更新后的 `schema_generator.py`
2. 更新后的单元测试
3. 所有测试通过的验证报告

