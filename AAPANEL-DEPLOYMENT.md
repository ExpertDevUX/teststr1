# StrophenBoost aaPanel Deployment Guide

## Prerequisites
- aaPanel installed on your VPS/server
- Root or sudo access
- Domain name pointed to your server

## Step 1: Prepare aaPanel Environment

### 1.1 Install Required Software in aaPanel
1. Login to your aaPanel dashboard
2. Go to **App Store** and install:
   - **Nginx** (Web server)
   - **PostgreSQL** (Database) 
   - **Python Manager** (Python 3.10+)
   - **Supervisor** (Process manager)

### 1.2 Create Database
1. Go to **Database** → **PostgreSQL**
2. Click **Add Database**
3. Database Name: `strophenboost`
4. Username: `strophenboost`
5. Password: `strophenboost123`
6. Click **Submit**

## Step 2: Upload and Setup Application

### 2.1 Upload Files
1. Go to **File Manager**
2. Navigate to `/www/wwwroot/`
3. Create folder: `strophenboost`
4. Upload all your project files to `/www/wwwroot/strophenboost/`

### 2.2 Install Python Dependencies
1. Go to **App Store** → **Python Manager**
2. Click **Add Project**
3. Project Name: `StrophenBoost`
4. Path: `/www/wwwroot/strophenboost`
5. Python Version: `3.10`
6. Click **Submit**

### 2.3 Install Packages
1. In Python Manager, click **Modules** for your project
2. Install these packages one by one:
```
flask==2.0.3
flask-sqlalchemy==2.5.1
flask-login==0.6.3
flask-socketio==5.3.6
flask-cors==4.0.0
flask-wtf==1.1.1
gunicorn==21.2.0
psycopg2-binary==2.9.7
email-validator==2.0.0
werkzeug==2.0.3
sqlalchemy==1.4.53
```

## Step 3: Configure Environment

### 3.1 Create Environment File
1. In File Manager, go to `/www/wwwroot/strophenboost/`
2. Create file: `.env`
3. Add content:
```
DATABASE_URL=postgresql://strophenboost:strophenboost123@localhost/strophenboost
SESSION_SECRET=your-random-secret-key-here
DOMAIN=yourdomain.com
```

### 3.2 Install System Dependencies
SSH into your server and run:
```bash
# Install FFmpeg for video processing
sudo apt update
sudo apt install ffmpeg -y

# Install additional dependencies
sudo apt install python3.10-dev postgresql-contrib -y
```

## Step 4: Configure Nginx

### 4.1 Create Website in aaPanel
1. Go to **Website** → **Add Site**
2. Domain: `yourdomain.com`
3. Root Directory: `/www/wwwroot/strophenboost`
4. PHP Version: **Pure Static** (we'll use Python)
5. Click **Submit**

### 4.2 Configure Nginx Proxy
1. Click **Settings** for your website
2. Go to **Config File**
3. Replace the content with:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Static files
    location /static {
        alias /www/wwwroot/strophenboost/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Stream output
    location /stream_output {
        alias /www/wwwroot/strophenboost/stream_output;
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range";
    }
}
```
4. Click **Save**

## Step 5: Configure Supervisor

### 5.1 Add Supervisor Configuration
1. SSH into your server
2. Create supervisor config:
```bash
sudo nano /etc/supervisor/conf.d/strophenboost.conf
```

3. Add content:
```ini
[program:strophenboost]
command=/www/server/python_manager/versions/3.10/bin/python -m gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 120 main:app
directory=/www/wwwroot/strophenboost
user=www
autostart=true
autorestart=true
stdout_logfile=/www/wwwroot/strophenboost/logs/app.log
stderr_logfile=/www/wwwroot/strophenboost/logs/app.log
environment=PATH="/www/server/python_manager/versions/3.10/bin:%(ENV_PATH)s"

[program:strophenboost-rtmp]
command=/www/server/python_manager/versions/3.10/bin/python start_rtmp_server.py
directory=/www/wwwroot/strophenboost
user=www
autostart=true
autorestart=true
stdout_logfile=/www/wwwroot/strophenboost/logs/rtmp.log
stderr_logfile=/www/wwwroot/strophenboost/logs/rtmp.log
environment=PATH="/www/server/python_manager/versions/3.10/bin:%(ENV_PATH)s"
```

### 5.2 Start Services
```bash
# Create logs directory
sudo mkdir -p /www/wwwroot/strophenboost/logs
sudo chown www:www /www/wwwroot/strophenboost/logs

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start strophenboost
sudo supervisorctl start strophenboost-rtmp
```

## Step 6: Setup SSL Certificate

### 6.1 Enable SSL in aaPanel
1. Go to your website settings
2. Click **SSL** tab
3. Select **Let's Encrypt**
4. Enter your email
5. Click **Apply**

### 6.2 Configure Firewall
1. Go to **Security** → **Firewall**
2. Add rules:
   - Port `80` (HTTP)
   - Port `443` (HTTPS)
   - Port `1935` (RTMP)

## Step 7: Initialize Database

SSH into your server and run:
```bash
cd /www/wwwroot/strophenboost
/www/server/python_manager/versions/3.10/bin/python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created')
"
```

## Step 8: Test Deployment

1. Visit `https://yourdomain.com`
2. You should see the StrophenBoost homepage
3. Register an account or login with admin credentials
4. Test RTMP streaming: `rtmp://yourdomain.com:1935/live`

## Troubleshooting

### Check Logs
```bash
# Application logs
tail -f /www/wwwroot/strophenboost/logs/app.log

# RTMP server logs
tail -f /www/wwwroot/strophenboost/logs/rtmp.log

# Supervisor status
sudo supervisorctl status
```

### Common Issues

1. **Permission Errors**: Ensure www user owns the files
```bash
sudo chown -R www:www /www/wwwroot/strophenboost
```

2. **Database Connection**: Check PostgreSQL is running in aaPanel

3. **Port Issues**: Ensure port 1935 is open for RTMP

4. **Python Path**: Verify Python 3.10 path in supervisor config

## Maintenance

### Update Application
1. Upload new files via aaPanel File Manager
2. Restart services:
```bash
sudo supervisorctl restart strophenboost
sudo supervisorctl restart strophenboost-rtmp
```

### Backup Database
```bash
sudo -u postgres pg_dump strophenboost > backup.sql
```

## Support

Your StrophenBoost streaming platform is now running on aaPanel with:
- Web interface at: `https://yourdomain.com`
- RTMP endpoint: `rtmp://yourdomain.com:1935/live`
- Admin dashboard for stream management
- Real-time chat and analytics