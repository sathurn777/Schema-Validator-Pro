# Schema Validator Pro - 部署指南

## 目录

- [1. 部署方式](#1-部署方式)
- [2. Docker 部署](#2-docker-部署)
- [3. Kubernetes 部署](#3-kubernetes-部署)
- [4. 环境变量配置](#4-环境变量配置)
- [5. 监控与告警](#5-监控与告警)
- [6. 故障排查](#6-故障排查)
- [7. 性能优化](#7-性能优化)

---

## 1. 部署方式

### 1.1 支持的部署方式

| 方式 | 适用场景 | 复杂度 |
|-----|---------|-------|
| **本地开发** | 开发测试 | 低 |
| **Docker** | 单机部署、容器化环境 | 中 |
| **Docker Compose** | 多服务编排（含数据库、Redis） | 中 |
| **Kubernetes** | 生产环境、高可用、自动扩缩容 | 高 |
| **云平台** | AWS ECS、Google Cloud Run、Azure Container Instances | 中 |

### 1.2 系统要求

**最低配置**：
- CPU: 1 核
- 内存: 512MB
- 磁盘: 1GB

**推荐配置（生产环境）**：
- CPU: 2-4 核
- 内存: 2-4GB
- 磁盘: 10GB

**软件依赖**：
- Python 3.9+
- pip
- (可选) Docker 20.10+
- (可选) Kubernetes 1.20+

---

## 2. Docker 部署

### 2.1 创建 Dockerfile

在项目根目录创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ ./backend/

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2.2 构建镜像

```bash
docker build -t schema-validator-pro:1.0.0 .
```

### 2.3 运行容器

```bash
docker run -d \
  --name schema-validator-pro \
  -p 8000:8000 \
  -e API_KEY=your-secret-key \
  -e ALLOWED_ORIGINS=https://yourdomain.com \
  -e SENTRY_DSN=your-sentry-dsn \
  -e ENVIRONMENT=production \
  schema-validator-pro:1.0.0
```

### 2.4 验证部署

```bash
# 检查容器状态
docker ps

# 查看日志
docker logs schema-validator-pro

# 健康检查
curl http://localhost:8000/health
```

---

## 3. Kubernetes 部署

### 3.1 创建 Deployment

创建 `k8s/deployment.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: schema-validator-pro
  labels:
    app: schema-validator-pro
spec:
  replicas: 3
  selector:
    matchLabels:
      app: schema-validator-pro
  template:
    metadata:
      labels:
        app: schema-validator-pro
    spec:
      containers:
      - name: schema-validator-pro
        image: schema-validator-pro:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: schema-validator-secrets
              key: api-key
        - name: ALLOWED_ORIGINS
          value: "https://yourdomain.com"
        - name: SENTRY_DSN
          valueFrom:
            secretKeyRef:
              name: schema-validator-secrets
              key: sentry-dsn
        - name: ENVIRONMENT
          value: "production"
        - name: MAX_REQUEST_SIZE
          value: "10485760"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

### 3.2 创建 Service

创建 `k8s/service.yaml`：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: schema-validator-pro
spec:
  selector:
    app: schema-validator-pro
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 3.3 创建 Secret

```bash
kubectl create secret generic schema-validator-secrets \
  --from-literal=api-key=your-secret-key \
  --from-literal=sentry-dsn=your-sentry-dsn
```

### 3.4 部署到 Kubernetes

```bash
# 应用配置
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 查看部署状态
kubectl get deployments
kubectl get pods
kubectl get services

# 查看日志
kubectl logs -f deployment/schema-validator-pro
```

### 3.5 配置 Horizontal Pod Autoscaler (HPA)

创建 `k8s/hpa.yaml`：

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: schema-validator-pro-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: schema-validator-pro
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

应用 HPA：

```bash
kubectl apply -f k8s/hpa.yaml
kubectl get hpa
```

---

## 4. 环境变量配置

### 4.1 必需环境变量

无必需环境变量，所有配置均有默认值。

### 4.2 可选环境变量

| 变量名 | 默认值 | 说明 |
|-------|-------|------|
| `API_KEY` | 无 | API Key 认证（未设置则不启用认证） |
| `ALLOWED_ORIGINS` | `http://localhost,http://localhost:8080` | CORS 允许的来源（逗号分隔） |
| `SENTRY_DSN` | 无 | Sentry 错误追踪 DSN |
| `ENVIRONMENT` | `development` | 环境名称（development/staging/production） |
| `SENTRY_SAMPLE_RATE` | `1.0` (生产) / `0.0` (开发) | Sentry 采样率 |
| `MAX_REQUEST_SIZE` | `10485760` (10MB) | 最大请求体大小（字节） |
| `ENABLE_METRICS` | `true` | 是否启用 Prometheus 指标 |

### 4.3 配置示例

**开发环境** (`.env.development`)：

```bash
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost,http://localhost:3000,http://localhost:8080
ENABLE_METRICS=true
```

**生产环境** (`.env.production`)：

```bash
API_KEY=your-production-secret-key
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
ENVIRONMENT=production
SENTRY_SAMPLE_RATE=1.0
MAX_REQUEST_SIZE=10485760
ENABLE_METRICS=true
```

### 4.4 加载环境变量

**方法 1：使用 .env 文件**

```bash
# 安装 python-dotenv
pip install python-dotenv

# 在 backend/main.py 中加载
from dotenv import load_dotenv
load_dotenv()
```

**方法 2：直接导出**

```bash
export API_KEY=your-secret-key
export ALLOWED_ORIGINS=https://yourdomain.com
```

**方法 3：Docker 运行时传递**

```bash
docker run -d \
  --env-file .env.production \
  schema-validator-pro:1.0.0
```

---

## 5. 监控与告警

### 5.1 Prometheus 指标

**启用指标**：

```bash
export ENABLE_METRICS=true
```

**访问指标端点**：

```bash
curl http://localhost:8000/metrics
```

**关键指标**：

| 指标名 | 类型 | 说明 |
|-------|------|------|
| `http_requests_total` | Counter | HTTP 请求总数 |
| `http_request_duration_seconds` | Histogram | 请求响应时间 |
| `schema_generation_total` | Counter | Schema 生成次数 |
| `schema_validation_total` | Counter | Schema 验证次数 |
| `schema_generation_success` | Counter | 成功生成次数 |
| `schema_generation_failure` | Counter | 失败生成次数 |

### 5.2 Prometheus 配置

创建 `prometheus.yml`：

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'schema-validator-pro'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

启动 Prometheus：

```bash
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### 5.3 Grafana 仪表板

**导入仪表板**：

1. 访问 Grafana (http://localhost:3000)
2. 添加 Prometheus 数据源
3. 导入仪表板 JSON（见下方示例）

**关键面板**：

- 请求速率（QPS）
- 响应时间（P50/P95/P99）
- 错误率
- Schema 生成成功率
- 完整度评分分布

### 5.4 Sentry 错误追踪

**配置 Sentry**：

```bash
export SENTRY_DSN=https://your-key@sentry.io/project-id
export ENVIRONMENT=production
export SENTRY_SAMPLE_RATE=1.0
```

**查看错误**：

1. 访问 Sentry 控制台
2. 查看 Issues 列表
3. 分析错误堆栈和上下文

**告警配置**：

在 Sentry 中配置告警规则：
- 错误率 > 1%
- 新错误类型出现
- 特定错误频率 > 10次/分钟

### 5.5 日志聚合

**结构化日志格式**：

```json
{
  "request_id": "uuid-here",
  "method": "POST",
  "path": "/api/v1/schema/generate",
  "status_code": 200,
  "duration_ms": 15.23,
  "event": "request_completed",
  "timestamp": "2025-10-26T10:00:00Z",
  "level": "info",
  "environment": "production"
}
```

**日志收集方案**：

- **ELK Stack**：Elasticsearch + Logstash + Kibana
- **Loki**：Grafana Loki + Promtail
- **Cloud Logging**：AWS CloudWatch、Google Cloud Logging

---

## 6. 故障排查

### 6.1 常见问题

#### 问题 1：容器启动失败

**症状**：

```bash
docker ps  # 容器不在运行列表中
```

**排查步骤**：

```bash
# 查看容器日志
docker logs schema-validator-pro

# 检查退出代码
docker inspect schema-validator-pro | grep ExitCode
```

**常见原因**：

- 端口冲突（8000 已被占用）
- 环境变量配置错误
- 依赖安装失败

**解决方案**：

```bash
# 更换端口
docker run -p 8001:8000 schema-validator-pro:1.0.0

# 检查环境变量
docker run --rm schema-validator-pro:1.0.0 env

# 重新构建镜像
docker build --no-cache -t schema-validator-pro:1.0.0 .
```

---

#### 问题 2：API 返回 500 错误

**症状**：

```json
{
  "error_code": "INTERNAL_ERROR",
  "message": "An unexpected error occurred"
}
```

**排查步骤**：

```bash
# 查看应用日志
docker logs -f schema-validator-pro

# 查看 Sentry 错误报告
# 访问 Sentry 控制台
```

**常见原因**：

- 内存不足
- 依赖库版本冲突
- 数据库连接失败（如果使用）

**解决方案**：

```bash
# 增加内存限制
docker run -m 2g schema-validator-pro:1.0.0

# 检查依赖版本
pip list

# 查看系统资源
docker stats
```

---

#### 问题 3：请求超时

**症状**：

```bash
curl: (28) Operation timed out after 30000 milliseconds
```

**排查步骤**：

```bash
# 检查服务是否运行
curl http://localhost:8000/health

# 查看响应时间
time curl http://localhost:8000/api/v1/schema/types

# 查看 Prometheus 指标
curl http://localhost:8000/metrics | grep duration
```

**常见原因**：

- 请求体过大
- 并发请求过多
- CPU/内存资源不足

**解决方案**：

```bash
# 增加 worker 数量
uvicorn backend.main:app --workers 8

# 增加超时时间
uvicorn backend.main:app --timeout-keep-alive 60

# 使用负载均衡
# 部署多个实例
```

---

#### 问题 4：CORS 错误

**症状**：

```
Access to fetch at 'http://localhost:8000/api/v1/schema/generate' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**解决方案**：

```bash
# 添加允许的来源
export ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# 或在 Docker 中
docker run -e ALLOWED_ORIGINS=http://localhost:3000 schema-validator-pro:1.0.0
```

---

### 6.2 性能问题排查

#### 慢查询分析

```bash
# 查看 Prometheus 指标
curl http://localhost:8000/metrics | grep http_request_duration

# 查看日志中的慢请求
docker logs schema-validator-pro | grep "duration_ms" | awk '$NF > 1000'
```

#### 内存泄漏检测

```bash
# 监控内存使用
docker stats schema-validator-pro

# 使用 memory_profiler
pip install memory_profiler
python -m memory_profiler backend/main.py
```

---

## 7. 性能优化

### 7.1 水平扩展

**Docker Compose**：

```yaml
version: '3.8'
services:
  schema-validator-pro:
    image: schema-validator-pro:1.0.0
    deploy:
      replicas: 4
    ports:
      - "8000-8003:8000"
```

**Kubernetes HPA**：

```bash
kubectl autoscale deployment schema-validator-pro \
  --cpu-percent=70 \
  --min=3 \
  --max=10
```

### 7.2 缓存策略

**Redis 缓存**（可选）：

```python
# 缓存 Schema 模板
import redis
r = redis.Redis(host='localhost', port=6379)

def get_template_cached(schema_type):
    cached = r.get(f"template:{schema_type}")
    if cached:
        return json.loads(cached)
    
    template = generator.get_template(schema_type)
    r.setex(f"template:{schema_type}", 3600, json.dumps(template))
    return template
```

### 7.3 数据库优化（如果使用）

- 添加索引
- 使用连接池
- 启用查询缓存

### 7.4 CDN 加速

对于静态资源（如文档、前端页面），使用 CDN 加速：

- Cloudflare
- AWS CloudFront
- Fastly

---

**文档版本**：1.0.0  
**最后更新**：2025-10-26  
**维护者**：Schema Validator Pro Team

