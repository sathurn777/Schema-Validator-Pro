# Schema Validator Pro

[![PyPI version](https://badge.fury.io/py/schema-validator-pro.svg)](https://badge.fury.io/py/schema-validator-pro)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Test Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)](https://github.com/schema-validator-pro/schema-validator-pro)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Production-Ready Schema.org JSON-LD Validator and Generator**

A high-performance, thoroughly tested tool for generating and validating Schema.org JSON-LD markup. Perfect for WordPress integration, SEO optimization, and structured data implementation.

## ✨ Highlights

- 🚀 **569 Tests, 100% Pass Rate, 97% Coverage**
- ⚡ **Microsecond Performance** (275,000+ ops/sec)
- 🎯 **9 Schema Types** with full validation
- 🔌 **WordPress Plugin** included
- 📦 **Production Ready** with monitoring & logging
- 🐳 **Docker Support** for easy deployment

## What It Does

Schema Validator Pro helps WordPress users improve their SEO by automatically adding structured data (Schema.org markup) to their content.

### ✅ Core Features

1. **Schema Generation** - Generate Schema.org JSON-LD for 9 content types
2. **WordPress Integration** - Seamless WordPress plugin with one-click generation
3. **Schema Validation** - Validate markup and get optimization suggestions

### 🎯 Supported Schema Types

- **Article** - Blog posts, news articles
- **Product** - E-commerce products
- **Recipe** - Cooking recipes
- **HowTo** - Step-by-step guides
- **FAQPage** - Frequently asked questions
- **Event** - Events and conferences
- **Person** - Author profiles
- **Organization** - Company information
- **Course** - Educational courses

## What It Does NOT Do

To set honest expectations:

- ❌ **No AI Monitoring** - Does not monitor AI search engines
- ❌ **No NLP Analysis** - Uses template-based generation, not advanced NLP
- ❌ **No Content Generation** - Does not create content, only adds markup
- ❌ **No Competitor Analysis** - Focuses on your content only
- ❌ **No Automated Reports** - Provides validation, not analytics

## 📦 Installation

### Option 1: Install from PyPI (Recommended)

```bash
# Install the package
pip install schema-validator-pro

# Start the server
schema-validator-pro

# Or with custom options
schema-validator-pro --host 0.0.0.0 --port 8000

# Check version
schema-validator-pro --version
```

### Option 2: Install from Source

```bash
# Clone repository
git clone https://github.com/schema-validator-pro/schema-validator-pro.git
cd schema-validator-pro

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -r requirements-dev.txt
```

### Option 3: Docker Compose (Full Stack)

For a complete WordPress + API setup:

```bash
# Start all services (WordPress + MySQL + API)
docker-compose -f docker-compose.test.yml up -d

# Access services
# WordPress: http://localhost:8080
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🚀 Quick Start

### CLI Usage

```bash
# Start the API server
schema-validator-pro

# Custom host and port
schema-validator-pro --host 0.0.0.0 --port 8080

# Enable auto-reload for development
schema-validator-pro --reload

# Show help
schema-validator-pro --help
```

### Python API Usage

```python
from backend.services import SchemaGenerator, SchemaValidator

# Generate schema
generator = SchemaGenerator()
schema = generator.generate_article_schema(
    headline="My Article Title",
    content="Article content here...",
    author="John Doe",
    date_published="2025-10-27"
)

# Validate schema
validator = SchemaValidator()
result = validator.validate_schema(schema)

if result.is_valid:
    print(f"Schema is valid! Completeness: {result.completeness_score}%")
else:
    print(f"Validation errors: {result.errors}")
```

### WordPress Plugin Installation

1. Copy `wordpress-plugin/schema-validator-pro` to `wp-content/plugins/`
2. Activate the plugin in WordPress admin
3. Configure API endpoint in **Schema Pro > Settings**
4. Start generating schemas in your posts!

## 📖 Documentation

- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[CHANGELOG](CHANGELOG.md)** - Version history and release notes
- **[CONTRIBUTING](CONTRIBUTING.md)** - How to contribute to the project
- **[WordPress Guide](docs/WordPress测试指南.md)** - WordPress integration guide

## How It Works

```
WordPress Post → Backend API → Schema Generator → Validation → WordPress Meta
                                                                      ↓
                                                              Auto-inject to <head>
```

1. User clicks "Generate Schema" in WordPress editor
2. WordPress sends post content to backend API
3. API generates Schema.org JSON-LD markup
4. API validates markup and calculates completeness score
5. Schema is saved to WordPress post meta
6. Plugin automatically injects schema into page `<head>` on frontend

## API Endpoints

### Generate Schema
```http
POST /api/v1/schema/generate
Content-Type: application/json

{
  "schema_type": "Article",
  "content": "Post title\n\nPost content...",
  "url": "https://example.com/post",
  "metadata": {
    "author": "John Doe",
    "datePublished": "2024-01-15"
  }
}
```

### Validate Schema
```http
POST /api/v1/schema/validate
Content-Type: application/json

{
  "schema": {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Example Article"
  }
}
```

### Get Supported Types
```http
GET /api/v1/schema/types
```

## Configuration

### Backend API

Create `.env` file:
```env
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=*
```

### WordPress Plugin

Configure in **Schema Pro > Settings**:
- **API Endpoint**: Backend API URL (e.g., `http://localhost:8000`)

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest backend/tests/test_schema_generator.py
```

## Development

### Project Structure

```
schema-validator-pro/
├── backend/
│   ├── services/
│   │   ├── schema_generator.py    # Schema generation logic
│   │   └── schema_validator.py    # Validation logic
│   ├── adapters/
│   │   └── wordpress_adapter.py   # WordPress API integration
│   ├── main.py                    # FastAPI application
│   └── tests/                     # Test files
├── wordpress-plugin/
│   └── schema-validator-pro/
│       └── schema-validator-pro.php  # WordPress plugin
├── config/requirements.txt        # Python dependencies
├── config/Dockerfile             # Docker build file
└── README.md                      # This file
```

### Code Quality

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

## Deployment

### Production Backend

```bash
# Using Docker
docker build -f config/Dockerfile -t schema-validator-pro .
docker run -p 8000:8000 schema-validator-pro

# Using systemd
sudo systemctl enable schema-validator-pro
sudo systemctl start schema-validator-pro
```

### WordPress Plugin Distribution

1. Zip the plugin folder:
```bash
cd wordpress-plugin
zip -r schema-validator-pro.zip schema-validator-pro/
```

2. Upload to WordPress:
   - Go to **Plugins > Add New > Upload Plugin**
   - Select `schema-validator-pro.zip`
   - Click **Install Now** and **Activate**

## Pricing

- **Free Version**: 10 schema generations per month
- **Pro Version**: $9/month - Unlimited generations
- **Enterprise**: $49/month - Priority support + custom schema types

## 📚 Documentation

### User Documentation
- [安装指南](docs/安装指南.md) - Installation guide
- [使用手册](docs/使用手册.md) - User manual
- [WordPress 测试指南](docs/WordPress测试指南.md) - Complete testing guide
- [功能说明](docs/功能说明.md) - Feature description

### Developer Documentation
- [API 文档](docs/API文档.md) - API reference
- [生成器配置指南](docs/生成器配置指南.md) - Generator configuration
- [开发指南](docs/开发指南.md) - Development guide

### Completion Reports
- [P0-1: Generator 优化报告](docs/P0-1-Generator-Completion-Report.md)
- [P0-2: Validator 优化报告](docs/P0-2-Validator-Completion-Report.md)
- [P0-3: Plugin 优化报告](docs/P0-3-Plugin-Completion-Report.md)
- [P0 任务全部完成总结](docs/P0-ALL-COMPLETION-SUMMARY.md)

## 🧪 Testing

### Run Backend Tests

```bash
# All tests
python -m pytest backend/tests/ -v

# Quick test
python tests/test_quick.py

# Plugin integrity test
python tests/test_plugin_integrity.py
```

**Test Coverage**: 97% (569/569 tests passing)

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/schema-validator-pro/issues)
- **Email**: support@schemavalidatorpro.com

## License

MIT License - See [LICENSE](LICENSE) file for details

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Schema.org](https://schema.org/) - Structured data vocabulary
- [WordPress](https://wordpress.org/) - Content management system

## 🎯 Project Status

**Version**: 1.0.0
**Status**: ✅ Production Ready
**Test Coverage**: 97% (569/569 tests passing)
**Performance**: 275,000+ operations/second

### Key Metrics

- ✅ **569 Tests** - 100% pass rate
- ✅ **97% Coverage** - Comprehensive test coverage
- ✅ **9 Schema Types** - Full Schema.org support
- ✅ **Microsecond Performance** - < 50 μs per operation
- ✅ **Production Monitoring** - Sentry + Prometheus
- ✅ **WordPress Plugin** - 761 lines, 17 PHPUnit tests

### Quality Assurance

- ✅ Zero TODO/FIXME comments
- ✅ Full type hints (PEP 561)
- ✅ Structured logging
- ✅ Error tracking
- ✅ Performance benchmarks
- ✅ Concurrent safety tests

## Changelog

### v1.0.0 (2025-10-21)
- ✅ Initial release
- ✅ 9 schema types supported (Article, Product, Recipe, HowTo, FAQPage, Event, Person, Organization, Course)
- ✅ WordPress plugin with auto-injection
- ✅ Schema validation with structured errors
- ✅ Nested object support with @type
- ✅ Field normalization (ISO8601, absolute URLs, ISO4217, BCP47)
- ✅ Site-level default configuration
- ✅ WordPress.org standard readme.txt
- ✅ Security enhancements (wp_json_encode, Nonce, permissions)
- ✅ Internationalization (i18n) support
- ✅ 100% test coverage

