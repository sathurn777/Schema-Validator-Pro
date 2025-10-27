# Schema Validator Pro - 文档中心

欢迎使用 Schema Validator Pro 文档中心。本项目是一个专业的 Schema.org JSON-LD 自动生成与验证工具，支持 WordPress 自动注入。

## 📚 文档导航

### 核心文档

- **[技术文档 (TECHNICAL.md)](./TECHNICAL.md)** - 系统架构、核心组件、数据流程、技术实现细节
- **[产品文档 (PRODUCT.md)](./PRODUCT.md)** - 产品概述、功能特性、用户指南、使用场景
- **[API 参考 (API_REFERENCE.md)](./API_REFERENCE.md)** - 完整的 API 端点文档、请求/响应示例
- **[部署指南 (DEPLOYMENT.md)](./DEPLOYMENT.md)** - 生产环境部署、配置、监控、故障排查

### 快速链接

- [快速开始](#快速开始)
- [支持的 Schema 类型](#支持的-schema-类型)
- [核心特性](#核心特性)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd schema-validator-pro_副本2
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 可选：API Key 认证
export API_KEY=your-secret-key

# 可选：CORS 配置
export ALLOWED_ORIGINS=http://localhost,https://yourdomain.com

# 可选：Sentry 错误追踪
export SENTRY_DSN=your-sentry-dsn
export ENVIRONMENT=production
```

### 3. 启动服务

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 验证安装

```bash
curl http://localhost:8000/health
```

---

## 📋 支持的 Schema 类型

Schema Validator Pro 支持以下 9 种 Schema.org 类型：

| Schema 类型 | 用途 | 必填字段 | 推荐字段 |
|------------|------|---------|---------|
| **Article** | 博客文章、新闻 | headline, datePublished, author | image, description |
| **Product** | 电商产品 | name, image | description, offers, brand |
| **Recipe** | 食谱 | name, recipeIngredient, recipeInstructions | image, cookTime |
| **Event** | 活动、会议 | name, startDate, location | endDate, organizer |
| **Organization** | 公司、组织 | name | url, logo, contactPoint |
| **Person** | 个人简介 | name | jobTitle, image, sameAs |
| **FAQPage** | 常见问题 | mainEntity | - |
| **HowTo** | 操作指南 | name, step | totalTime, tool |
| **Course** | 在线课程 | name, description, provider | - |

---

## ✨ 核心特性

### 1. 自动生成 Schema
- 基于内容自动提取关键信息
- 智能填充必填和推荐字段
- 支持嵌套结构（如 Product.offers、Recipe.nutrition）

### 2. 智能验证
- 必填字段检查
- 推荐字段检查
- 嵌套结构验证
- 完整度评分（0-100%）
- 优化建议生成

### 3. 结构化错误输出
- 支持 `structured=true` 模式
- 包含字段路径（JSON Path）
- 错误代码（Error Code）
- 严重级别（ERROR/WARNING）

### 4. WordPress 集成
- 自动注入到 WordPress 文章/页面
- 支持 Application Password 认证
- 自动更新现有 Schema

### 5. 生产级特性
- **性能**：微秒级操作（1.4-3000 μs）
- **并发**：支持高并发请求
- **监控**：Prometheus 指标 + Sentry 错误追踪
- **安全**：API Key 认证、输入验证、请求大小限制
- **测试**：569 个测试，97.32% 覆盖率

---

## 📊 项目状态

- **版本**：1.0.0
- **测试覆盖率**：97.32%
- **测试数量**：569 个（100% 通过）
- **性能基准**：1.4-3000 μs（微秒级）
- **支持的 Schema 类型**：9 种
- **API 端点**：9 个

---

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Generate │  │ Validate │  │ Template │  │ Metrics │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   Middleware Stack                       │
│  Request Size → Logging → Metrics → Auth → CORS         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    Service Layer                         │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │ SchemaGenerator  │  │ SchemaValidator  │            │
│  └──────────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Registry & Adapters                     │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │ SchemaRegistry   │  │ WordPressAdapter │            │
│  └──────────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

---

## 📖 文档详细说明

### [技术文档 (TECHNICAL.md)](./TECHNICAL.md)

适合开发者、架构师阅读，包含：
- 系统架构设计
- 核心组件实现细节
- 依赖注入（DI）模式
- 数据流程图（Mermaid）
- 测试策略
- 性能优化

### [产品文档 (PRODUCT.md)](./PRODUCT.md)

适合产品经理、用户阅读，包含：
- 产品价值与应用场景
- 功能特性列表
- 用户指南与示例
- 最佳实践
- 常见问题解答

### [API 参考 (API_REFERENCE.md)](./API_REFERENCE.md)

适合集成开发者阅读，包含：
- 所有 API 端点详细说明
- 请求/响应格式
- 错误码参考
- 代码示例（curl、Python、JavaScript）

### [部署指南 (DEPLOYMENT.md)](./DEPLOYMENT.md)

适合运维工程师阅读，包含：
- Docker 部署
- Kubernetes 部署
- 环境变量配置
- 监控与告警
- 故障排查

---

## 🤝 贡献指南

欢迎贡献代码、文档或报告问题！

### 开发流程

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

### 测试要求

- 所有新功能必须有单元测试
- 测试覆盖率必须 ≥97%
- 所有测试必须通过

```bash
# 运行测试
python -m pytest backend/tests/ --cov=backend --cov-fail-under=97 -p no:asyncio

# 运行性能测试
python -m pytest backend/tests/test_performance_benchmarks.py -v
```

---

## 📞 支持与反馈

- **问题反馈**：提交 GitHub Issue
- **功能建议**：提交 Feature Request
- **安全问题**：发送邮件至 security@example.com

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](../LICENSE) 文件。

---

**最后更新**：2025-10-26  
**文档版本**：1.0.0

