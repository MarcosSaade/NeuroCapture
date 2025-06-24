# NeuroCapture Deployment Guide

This guide covers deploying NeuroCapture in production environments.

## Deployment Options

### Option 1: Desktop Application (Recommended)
Package as standalone desktop application for researchers and clinicians.

## Desktop Application Deployment

### Building the Application

#### Prerequisites
- Node.js 18+
- Python 3.8+
- Platform-specific build tools

#### Build Process

1. **Prepare Backend**
   ```bash
   cd backend
   
   # Install production dependencies
   pip install -r requirements.txt --no-dev
   
   # Run database migrations
   alembic upgrade head
   
   # Create standalone backend executable (optional)
   pip install pyinstaller
   pyinstaller --onefile --add-data "app:app" app/main.py
   ```

2. **Build Frontend**
   ```bash
   cd frontend
   
   # Install dependencies
   npm ci --production
   
   # Build renderer process
   npm run build:renderer
   
   # Package Electron application
   npm install electron-builder --save-dev
   npm run build:electron
   ```

#### Electron Builder Configuration

Add to `frontend/package.json`:
```json
{
  "build": {
    "appId": "com.neurocapture.app",
    "productName": "NeuroCapture",
    "directories": {
      "output": "dist"
    },
    "files": [
      "main/**/*",
      "renderer/dist/**/*",
      "node_modules/**/*"
    ],
    "win": {
      "target": "nsis",
      "icon": "assets/icon.ico"
    },
    "mac": {
      "target": "dmg",
      "icon": "assets/icon.icns"
    },
    "linux": {
      "target": "AppImage",
      "icon": "assets/icon.png"
    }
  }
}
```

#### Platform-Specific Builds

**Windows**:
```bash
npm run build:win
```

**macOS**:
```bash
npm run build:mac
```

**Linux**:
```bash
npm run build:linux
```

### Distribution

#### Code Signing (Recommended)
- **Windows**: Use Authenticode certificate
- **macOS**: Use Apple Developer certificate
- **Linux**: Use GPG signing

#### Installer Creation
- **Windows**: NSIS installer with auto-update
- **macOS**: DMG with drag-to-Applications
- **Linux**: AppImage for portability

## Server Deployment

### Backend API Server

#### Environment Setup

1. **Create Production Environment**
   ```bash
   # Create .env.production
   DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/neurocapture
   DEBUG=false
   CORS_ORIGINS=https://your-domain.com
   UPLOAD_DIRECTORY=/app/uploads
   LOG_LEVEL=INFO
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install gunicorn  # Production WSGI server
   ```

3. **Database Setup**
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Create indexes for performance
   psql -h db-host -U user -d neurocapture -f scripts/create_indexes.sql
   ```

#### Production Server Configuration

**Using Gunicorn**:
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --keep-alive 5 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

**Systemd Service** (`/etc/systemd/system/neurocapture.service`):
```ini
[Unit]
Description=NeuroCapture API
After=network.target

[Service]
Type=exec
User=neurocapture
Group=neurocapture
WorkingDirectory=/opt/neurocapture
Environment=PATH=/opt/neurocapture/venv/bin
EnvironmentFile=/opt/neurocapture/.env.production
ExecStart=/opt/neurocapture/venv/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Nginx Reverse Proxy

**Configuration** (`/etc/nginx/sites-available/neurocapture`):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Handle large audio uploads
        client_max_body_size 100M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Static files (audio recordings)
    location /uploads/ {
        alias /opt/neurocapture/uploads/;
        expires 1h;
        add_header Cache-Control "public, no-transform";
    }
    
    # Documentation
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

### Database Deployment

#### PostgreSQL Production Setup

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   
   # Create database and user
   sudo -u postgres psql
   CREATE DATABASE neurocapture;
   CREATE USER neurocapture WITH ENCRYPTED PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE neurocapture TO neurocapture;
   ```

2. **Performance Tuning** (`postgresql.conf`):
   ```conf
   # Memory settings
   shared_buffers = 256MB
   effective_cache_size = 1GB
   work_mem = 4MB
   maintenance_work_mem = 64MB
   
   # Checkpoint settings
   checkpoint_completion_target = 0.9
   wal_buffers = 16MB
   
   # Query planner
   random_page_cost = 1.1
   effective_io_concurrency = 200
   ```

3. **Create Indexes** (`scripts/create_indexes.sql`):
   ```sql
   -- Patient search optimization
   CREATE INDEX CONCURRENTLY idx_patients_study_identifier 
   ON patients(study_identifier);
   
   -- Assessment queries
   CREATE INDEX CONCURRENTLY idx_assessments_patient_date 
   ON cognitive_assessments(patient_id, assessment_date);
   
   -- Audio feature queries
   CREATE INDEX CONCURRENTLY idx_features_recording_name 
   ON audio_features(recording_id, feature_name);
   
   -- Demographic queries
   CREATE INDEX CONCURRENTLY idx_demographics_patient 
   ON demographics(patient_id);
   ```

#### Backup Strategy

**Automated Backup Script** (`scripts/backup.sh`):
```bash
#!/bin/bash
set -e

BACKUP_DIR="/opt/backups/neurocapture"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="neurocapture"
DB_USER="neurocapture"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Database backup
pg_dump -h localhost -U "$DB_USER" -d "$DB_NAME" \
  --verbose --clean --no-owner --no-privileges \
  | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Upload directory backup
tar -czf "$BACKUP_DIR/uploads_backup_$DATE.tar.gz" \
  /opt/neurocapture/uploads/

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Cron Job** (`crontab -e`):
```bash
# Daily backup at 2 AM
0 2 * * * /opt/neurocapture/scripts/backup.sh >> /var/log/neurocapture-backup.log 2>&1
```

## Docker Deployment

### Production Docker Compose

**`docker-compose.prod.yml`**:
```yaml
version: "3.9"

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: neurocapture-db-prod
    restart: unless-stopped
    environment:
      POSTGRES_DB: neurocapture
      POSTGRES_USER: neurocapture
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./backup:/backup
    networks:
      - neurocapture_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U neurocapture"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backend API
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: neurocapture-api-prod
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql+asyncpg://neurocapture:${DB_PASSWORD}@db:5432/neurocapture
      DEBUG: "false"
      LOG_LEVEL: INFO
    volumes:
      - uploads_data:/app/uploads
      - ./logs:/app/logs
    networks:
      - neurocapture_network
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: neurocapture-nginx-prod
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - uploads_data:/usr/share/nginx/html/uploads:ro
    networks:
      - neurocapture_network
    depends_on:
      - api

secrets:
  db_password:
    file: ./secrets/db_password.txt

volumes:
  db_data:
    name: neurocapture_db_data_prod
  uploads_data:
    name: neurocapture_uploads_prod

networks:
  neurocapture_network:
    name: neurocapture_network_prod
```

### Backend Dockerfile

**`backend/Dockerfile.prod`**:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r neurocapture && useradd -r -g neurocapture neurocapture

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs && \
    chown -R neurocapture:neurocapture /app

# Switch to non-root user
USER neurocapture

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120"]
```

### Deployment Commands

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Update application
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --no-deps api

# Backup
docker-compose -f docker-compose.prod.yml exec db \
  pg_dump -U neurocapture neurocapture | gzip > backup_$(date +%Y%m%d).sql.gz
```

## Monitoring and Logging

### Application Monitoring

#### Health Checks

Add to `app/main.py`:
```python
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        async with async_session() as db:
            await db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Health check failed: {str(e)}"
        )
```

#### Logging Configuration

**`app/core/logging.py`**:
```python
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(log_level: str = "INFO"):
    """Configure application logging."""
    
    # Create logger
    logger = logging.getLogger("neurocapture")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        "logs/neurocapture.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
```

### Performance Monitoring

#### Database Performance

**Slow Query Monitoring** (`postgresql.conf`):
```conf
log_min_duration_statement = 1000  # Log queries > 1 second
log_statement = 'mod'              # Log data-modifying statements
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

#### Application Metrics

**Basic Metrics Collection** (`app/middleware/metrics.py`):
```python
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log metrics
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Duration: {process_time:.3f}s"
        )
        
        return response
```

## Security Considerations

### Network Security
- Use HTTPS in production
- Configure firewall rules
- VPN access for remote connections
- Regular security updates

### Data Protection
- Encrypt sensitive data at rest
- Secure backup storage
- Access logging and auditing
- HIPAA compliance considerations

### Application Security
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)
- File upload restrictions
- Error message sanitization

## Scaling Considerations

### Horizontal Scaling
- Load balancer for multiple API instances
- Read replicas for database
- Distributed file storage
- Session state management

### Performance Optimization
- Database connection pooling
- Caching with Redis
- CDN for static files
- Async processing for heavy tasks

## Troubleshooting

### Common Issues

**Database Connection Errors**:
```bash
# Check database status
docker-compose ps db

# View database logs
docker-compose logs db

# Test connection
psql -h localhost -U neurocapture -d neurocapture -c "SELECT version();"
```

**Application Errors**:
```bash
# View application logs
docker-compose logs api

# Debug mode
docker-compose -f docker-compose.prod.yml \
  exec api python -c "import app.main; print('Import successful')"
```

**Performance Issues**:
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check database size
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

For technical support during deployment, refer to the [DOCUMENTATION.md](DOCUMENTATION.md) and [DEVELOPMENT.md](DEVELOPMENT.md) guides.
