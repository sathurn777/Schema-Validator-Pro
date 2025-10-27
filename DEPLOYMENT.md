# Schema Validator Pro - Deployment Guide

This guide covers deploying the Schema Validator Pro backend service in production.

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit configuration (CRITICAL!)
nano .env
# Set ALLOWED_ORIGINS to your WordPress domain
# Set DEBUG=false
# Set APP_ENV=production

# 3. Start services
docker-compose -f docker-compose.prod.yml up -d

# 4. Check status
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Option 2: Systemd Service (Linux)

```bash
# 1. Run installation script as root
sudo bash scripts/install.sh

# 2. Configure environment
sudo nano /opt/schema-validator-pro/.env

# 3. Enable and start service
sudo systemctl enable schema-validator-pro
sudo systemctl start schema-validator-pro

# 4. Check status
sudo systemctl status schema-validator-pro
sudo journalctl -u schema-validator-pro -f
```

### Option 3: Manual Start

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r config/requirements.txt

# 3. Configure environment
cp .env.example .env
nano .env

# 4. Start server
bash scripts/start.sh
```

---

## ⚙️ Configuration

### Critical Environment Variables

**MUST configure these for production:**

```bash
# SECURITY: Set to your WordPress domain(s)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# SECURITY: Disable debug mode
DEBUG=false

# Set environment
APP_ENV=production

# Optional but recommended: API authentication
API_KEY=your-secret-key-here
```

### Optional Configuration

```bash
# Performance
ENABLE_CACHE=true
CACHE_TTL=3600
RATE_LIMIT=60

# Logging
LOG_LEVEL=INFO
ENABLE_REQUEST_LOGGING=true

# Monitoring (optional)
SENTRY_DSN=https://your-sentry-dsn
```

---

## 🔒 Security Checklist

Before deploying to production, verify:

- [ ] `ALLOWED_ORIGINS` is set to specific domains (NOT `*`)
- [ ] `DEBUG=false` in .env
- [ ] `APP_ENV=production` in .env
- [ ] SSL/TLS certificate configured (use nginx reverse proxy)
- [ ] Firewall configured (allow only necessary ports)
- [ ] `.env` file permissions set to 600
- [ ] API authentication enabled (optional but recommended)
- [ ] Regular security updates scheduled

---

## 🌐 Nginx Reverse Proxy (Recommended)

Create `/etc/nginx/sites-available/schema-validator-pro`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/schema-validator-pro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "schema_generator": "ok",
    "schema_validator": "ok"
  },
  "supported_types": ["Article", "Product", ...]
}
```

### Logs

**Docker:**
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
```

**Systemd:**
```bash
sudo journalctl -u schema-validator-pro -f
```

**Manual:**
```bash
tail -f logs/uvicorn.log
```

### Metrics (Optional)

Add Prometheus metrics:
```bash
pip install prometheus-fastapi-instrumentator
```

---

## 🔄 Updates

### Docker

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Systemd

```bash
# Pull latest changes
cd /opt/schema-validator-pro
sudo git pull

# Restart service
sudo systemctl restart schema-validator-pro
```

---

## 🐛 Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u schema-validator-pro -n 50

# Check configuration
sudo cat /opt/schema-validator-pro/.env

# Test manually
cd /opt/schema-validator-pro
source venv/bin/activate
python -m backend.main
```

### CORS errors

Verify `ALLOWED_ORIGINS` in `.env`:
```bash
ALLOWED_ORIGINS=https://yourdomain.com
```

### Permission denied

```bash
sudo chown -R www-data:www-data /opt/schema-validator-pro
sudo chmod 600 /opt/schema-validator-pro/.env
```

---

## 📞 Support

- **Documentation**: [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/schemavalidatorpro/schema-validator-pro/issues)
- **Security**: Report security issues privately

---

## 📝 Production Checklist

Before going live:

- [ ] Backend deployed and running
- [ ] Health check returns 200 OK
- [ ] SSL/TLS configured
- [ ] CORS configured correctly
- [ ] Firewall rules applied
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] WordPress plugin configured with correct API endpoint
- [ ] End-to-end test completed
- [ ] Load testing completed (optional)

