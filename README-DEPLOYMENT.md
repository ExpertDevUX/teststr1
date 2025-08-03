# StrophenBoost VPS Deployment Guide

## Quick Setup for Your VPS

**IMPORTANT:** Use the Python installer, not the bash script.

### Step 1: Upload Files
Upload all your project files to your VPS server.

### Step 2: Run Python Installer
```bash
python3 install.py
```

### What the installer does:
- ✅ Detects if this is a new install or update
- ✅ Installs Python 3.10, PostgreSQL, Nginx, FFmpeg
- ✅ Creates strophenboost user and database
- ✅ Sets up virtual environment and dependencies
- ✅ Configures Supervisor for service management
- ✅ Sets up Nginx with SSL certificates
- ✅ Configures firewall rules
- ✅ Starts your streaming platform

### For New Installations:
The installer will ask for:
- Your domain name
- Your email address (for SSL certificates)

### For Updates:
Just run `python3 install.py` - it will automatically:
- Create a backup of your current installation
- Update all files
- Restart services

### After Installation:
- **Web Interface:** https://yourdomain.com
- **RTMP URL:** rtmp://yourdomain.com:1935/live
- **Logs:** /var/log/strophenboost/
- **App Directory:** /opt/strophenboost

### Troubleshooting:
If you get any errors, check the logs:
```bash
sudo tail -f /var/log/strophenboost/app.log
sudo tail -f /var/log/strophenboost/rtmp.log
```

### Service Management:
```bash
# Check status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart strophenboost
sudo supervisorctl restart strophenboost-rtmp

# Restart web server
sudo systemctl restart nginx
```

## Why Python Instead of Bash?

The Python installer (`install.py`) works reliably across all VPS environments because:
- No bash version compatibility issues
- Proper error handling and recovery
- Clear progress feedback
- Works on any Ubuntu/Debian VPS

**Always use `python3 install.py` for deployment!**