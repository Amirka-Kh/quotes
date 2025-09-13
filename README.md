# Quotello

Find Your Favorite Words of Wisdom. A dynamic platform where the community decides the most inspiring and powerful quotes through votes. Below you can see the quide about application deployment.

This guide covers deploying the Django Quotes Application to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
- [Manual Deployment](#manual-deployment)
- [SSL Configuration](#ssl-configuration)
- [Monitoring](#monitoring)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+ or CentOS 8+ (recommended)
- **RAM**: Minimum 1GB, recommended 2GB+
- **Storage**: Minimum 2GB free space
- **Network**: Ports 80, 443, and 22 open

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Git
- SSL certificate (for HTTPS)

## Environment Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login to apply Docker group changes
```

### 2. Application Setup

```bash
# Clone repository
git clone <your-repository-url>
cd django-quotes

# Create environment file
cp env.template .env
```

### 3. Configure Environment Variables

Edit `.env` file with your production values:

```bash
# Django Configuration
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Docker Deployment

### 1. Production Deployment

```bash
# Build and start services
make prod
# or
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 2. Health Check

```bash
# Check application health
curl http://localhost/quotes/health/

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "database": "connected",
  "cache": "connected",
  "quotes_count": 42
}
```

### 3. SSL Configuration

For HTTPS deployment:

1. **Obtain SSL Certificate**
   ```bash
   # Using Let's Encrypt (recommended)
   sudo apt install certbot
   sudo certbot certonly --standalone -d yourdomain.com
   ```

2. **Update Nginx Configuration**
   ```bash
   # Copy SSL certificates
   sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
   sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
   
   # Update docker-compose.prod.yml to use SSL config
   # Change nginx config volume to: ./nginx/nginx-ssl.conf:/etc/nginx/nginx.conf:ro
   ```

3. **Restart Services**
   ```bash
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

## Manual Deployment

### 1. System Dependencies

```bash
# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3.11-dev
sudo apt install nginx postgresql-client

# Create application user
sudo useradd -m -s /bin/bash quotes
sudo usermod -aG www-data quotes
```

### 2. Application Setup

```bash
# Switch to application user
sudo su - quotes

# Clone and setup application
git clone <repository-url> /home/quotes/app
cd /home/quotes/app

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.template .env
# Edit .env with production values

# Run setup
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py production_setup --migrate --collect-static
```

### 3. Systemd Service

```bash
# Copy service file
sudo cp scripts/django-quotes.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable django-quotes
sudo systemctl start django-quotes
sudo systemctl status django-quotes
```

### 4. Nginx Configuration

```bash
# Copy Nginx configuration
sudo cp nginx/nginx.conf /etc/nginx/sites-available/django-quotes
sudo ln -s /etc/nginx/sites-available/django-quotes /etc/nginx/sites-enabled/

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

## Monitoring

### 1. Application Monitoring

```bash
# Check application logs
docker-compose -f docker-compose.prod.yml logs -f app

# Check Nginx logs
docker-compose -f docker-compose.prod.yml logs -f nginx

# Monitor resource usage
docker stats
```

### 2. Health Monitoring

Set up monitoring for the health endpoint:

```bash
# Simple health check script
#!/bin/bash
HEALTH_URL="http://localhost/quotes/health/"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ Application is healthy"
else
    echo "❌ Application health check failed (HTTP $RESPONSE)"
    # Add alerting logic here
fi
```

### 3. Log Monitoring

```bash
# Monitor error logs
tail -f logs/error.log

# Monitor access logs
tail -f logs/django.log

# Log rotation (add to crontab)
0 0 * * * /usr/sbin/logrotate /etc/logrotate.d/django-quotes
```

## Maintenance

### 1. Regular Backups

```bash
# Database backup
./scripts/backup.sh

# Full application backup
tar -czf backup-$(date +%Y%m%d).tar.gz \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    .
```

### 2. Updates

```bash
# Update application
./scripts/update.sh

# Or manual update
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Database Maintenance

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec app python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec app python manage.py createsuperuser

# Check deployment readiness
docker-compose -f docker-compose.prod.yml exec app python manage.py production_setup --check-deploy
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs app

# Common causes:
# - Missing environment variables
# - Database connection issues
# - Port conflicts
```

#### 2. Static Files Not Loading

```bash
# Check static file collection
docker-compose -f docker-compose.prod.yml exec app python manage.py collectstatic --noinput

# Check Nginx configuration
docker-compose -f docker-compose.prod.yml logs nginx
```

#### 3. Database Issues

```bash
# Check database connection
docker-compose -f docker-compose.prod.yml exec app python manage.py dbshell

# Run migrations
docker-compose -f docker-compose.prod.yml exec app python manage.py migrate
```

#### 4. SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Renew Let's Encrypt certificate
sudo certbot renew
```

### Performance Issues

#### 1. High Memory Usage

```bash
# Check memory usage
docker stats

# Optimize Gunicorn workers
# Edit gunicorn.conf.py and reduce worker count
```

#### 2. Slow Response Times

```bash
# Check Nginx logs for slow requests
grep "slow" /var/log/nginx/access.log

# Enable Nginx caching
# Add caching directives to nginx configuration
```

### Security Issues

#### 1. Check Security Headers

```bash
# Test security headers
curl -I https://yourdomain.com

# Should include:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
```

#### 2. SSL Configuration

```bash
# Test SSL configuration
openssl s_client -connect yourdomain.com:443

# Check SSL rating
# Visit: https://www.ssllabs.com/ssltest/
```

## Support

For additional support:

1. Check the application logs
2. Review the troubleshooting section
3. Create an issue in the repository
4. Check the health endpoint: `/quotes/health/`

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Backup strategy in place
- [ ] Health monitoring configured


