# Deployment Guide

**Intelligent Resume Parser - AI-Powered Resume Analysis & Extraction Platform**  
**GEMINI SOLUTION**

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **CPU:** 2+ cores recommended
- **RAM:** Minimum 2GB, 4GB+ recommended
- **Disk Space:** 10GB+ (for models and database)
- **OS:** Linux, macOS, or Windows (with WSL/Docker)

### Software Requirements

- **Python:** 3.8 or higher
- **Docker:** 20.10+ (for containerized deployment)
- **Docker Compose:** 1.29+ (for multi-container setup)
- **PostgreSQL:** 15+ (optional, SQLite works for development)

---

## Local Development Setup

### Quick Start

```bash
# 1. Clone repository
git clone <repository-url>
cd resume-parser

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Start server
source venv/bin/activate
python simple_start.py
```

### Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env

# 4. Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response: {"status":"healthy"}
```

---

## Docker Deployment

### Quick Start with Docker Compose

```bash
# 1. Navigate to docker directory
cd docker

# 2. Start all services
docker-compose up -d

# 3. Check logs
docker-compose logs -f api

# 4. Verify health
curl http://localhost:8000/health
```

### Docker Services

The `docker-compose.yml` includes:

1. **PostgreSQL Database** (port 5432)
   - User: `resume_user`
   - Password: `resume_pass`
   - Database: `resume_parser`

2. **API Service** (port 8000)
   - Auto-rebuilds on code changes
   - Connects to PostgreSQL
   - Persistent model storage

### Building Docker Image

```bash
# Build image
docker build -t resume-parser:latest -f docker/Dockerfile .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  resume-parser:latest
```

---

## Production Deployment

### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Clone Repository

```bash
# Clone repository
git clone <repository-url>
cd resume-parser

# Create production .env
cat > docker/.env << EOF
DATABASE_URL=postgresql://resume_user:STRONG_PASSWORD@db:5432/resume_parser
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
MODEL_CACHE_DIR=/app/models
USE_GPU=false
EOF
```

### Step 3: Deploy with Docker Compose

```bash
cd docker

# Start services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 4: Setup Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/resume-parser
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/resume-parser /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: Setup SSL (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Environment Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/resume_parser
# Or for SQLite: DATABASE_URL=sqlite:///./resume_parser.db

# Environment
ENVIRONMENT=production  # or development

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Model Cache
MODEL_CACHE_DIR=./models

# GPU Support
USE_GPU=false  # Set to true if CUDA available

# Optional: External Services
# OPENAI_API_KEY=your_key_here
# HUGGINGFACE_TOKEN=your_token_here
```

### Production Security

```env
# Strong database password
DATABASE_URL=postgresql://resume_user:CHANGE_THIS_PASSWORD@db:5432/resume_parser

# Environment
ENVIRONMENT=production

# Disable debug mode
DEBUG=false

# API Keys
API_KEY=generate_strong_random_key
```

---

## Database Setup

### PostgreSQL Setup

```bash
# Create database
sudo -u postgres psql
CREATE DATABASE resume_parser;
CREATE USER resume_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE resume_parser TO resume_user;
\q
```

### Run Migrations

```bash
# With Docker
docker-compose exec api alembic upgrade head

# Local
alembic upgrade head
```

### Database Backups

```bash
# Backup
docker-compose exec db pg_dump -U resume_user resume_parser > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T db psql -U resume_user resume_parser < backup_20240101.sql
```

---

## Monitoring & Maintenance

### Health Monitoring

```bash
# Check API health
curl http://localhost:8000/health

# Check detailed health
curl http://localhost:8000/api/v1/resumes/health/check
```

### Log Monitoring

```bash
# Docker logs
docker-compose logs -f api

# Application logs
tail -f logs/app.log
```

### Performance Monitoring

```bash
# Check resource usage
docker stats

# Database connections
docker-compose exec db psql -U resume_user -d resume_parser -c "SELECT count(*) FROM pg_stat_activity;"
```

### Maintenance Tasks

```bash
# Update dependencies
docker-compose exec api pip install --upgrade -r requirements.txt

# Restart services
docker-compose restart

# Clean up old containers
docker-compose down
docker system prune -a
```

---

## Troubleshooting

### Issue: Container won't start

```bash
# Check logs
docker-compose logs api

# Common fixes
docker-compose down
docker-compose up -d --build
```

### Issue: Database connection error

```bash
# Check database is running
docker-compose ps db

# Test connection
docker-compose exec db pg_isready -U resume_user

# Restart database
docker-compose restart db
```

### Issue: Port already in use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

### Issue: Out of memory

```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Edit Docker Desktop settings or docker daemon.json
```

### Issue: Models not loading

```bash
# Check model directory permissions
docker-compose exec api ls -la /app/models

# Re-download models
docker-compose exec api python -m spacy download en_core_web_sm
```

---

## Scaling

### Horizontal Scaling

```bash
# Scale API service
docker-compose up -d --scale api=3

# Use load balancer (Nginx)
upstream api_servers {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}
```

### Database Scaling

- Use PostgreSQL replication
- Implement read replicas
- Connection pooling (already configured)

---

## Backup Strategy

### Automated Backups

```bash
# Create backup script
cat > /usr/local/bin/backup-resume-parser.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U resume_user resume_parser > /backups/resume_parser_$DATE.sql
find /backups -name "resume_parser_*.sql" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup-resume-parser.sh

# Add to crontab (daily at 2 AM)
0 2 * * * /usr/local/bin/backup-resume-parser.sh
```

---

## Security Checklist

- [ ] Change default database passwords
- [ ] Use strong API keys
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable authentication
- [ ] Regular security updates
- [ ] Database backups configured
- [ ] Log monitoring enabled
- [ ] Error tracking set up

---

## Support

For deployment issues:
- Check logs: `docker-compose logs -f`
- Review documentation: `README.md`
- Test health: `curl http://localhost:8000/health`

**Developer:** JAYANT SHARMA  
**Roll No:** CO24529  
**Email:** co24529@ccet.ac.in  
**Organization:** GEMINI SOLUTION

