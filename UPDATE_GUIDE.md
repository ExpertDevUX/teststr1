# StrophenBoost Update Script - Troubleshooting Guide

## Issue: Bash Syntax Errors on VPS

### Problem Description
The update script is encountering syntax errors when transferred to VPS servers, particularly with constructs like `|| true` and single-line if statements.

### Root Cause
- File transfer corruption (line endings, encoding issues)
- Older or stricter bash versions on VPS systems
- Shell compatibility differences between development and production environments

### Solution: Ultra-Compatible Script

Use `update_simple.sh` which has been designed for maximum compatibility:

```bash
# Download and test the ultra-compatible version
chmod +x update_simple.sh
bash -n update_simple.sh  # Test syntax
sudo ./update_simple.sh  # Run update
```

### Key Differences in Compatible Version

1. **Removed `|| true` constructs** - Replaced with explicit error handling
2. **Simplified command chaining** - Used separate commands instead of `&&` chains
3. **Traditional if-then-fi format** - Multi-line format for all conditionals
4. **Explicit error checking** - Manual exit code checks instead of bash shortcuts
5. **Removed `set -o pipefail`** - Some older systems don't support this

### Manual Update Process (If Scripts Fail)

If all scripts fail, you can update manually:

```bash
# 1. Stop services
sudo supervisorctl stop strophenboost strophenboost-rtmp

# 2. Backup current installation
sudo cp -r /opt/strophenboost /opt/strophenboost-backup-$(date +%Y%m%d)

# 3. Update system packages
sudo apt update && sudo apt upgrade -y

# 4. Update Python dependencies
cd /opt/strophenboost
sudo -u strophenboost bash -c "source venv/bin/activate && pip install --upgrade flask==2.0.3 flask-sqlalchemy==2.5.1 flask-login==0.6.3 flask-socketio==5.3.6 flask-cors==4.0.0 flask-wtf==1.1.1 gunicorn==21.2.0 psycopg2-binary==2.9.7 email-validator==2.0.0 werkzeug==2.0.3 sqlalchemy==1.4.53"

# 5. Copy files manually
sudo cp ~/stropenboost.github.io/*.py /opt/strophenboost/
sudo cp ~/stropenboost.github.io/pyproject.toml /opt/strophenboost/
sudo cp -r ~/stropenboost.github.io/templates /opt/strophenboost/
sudo cp -r ~/stropenboost.github.io/static /opt/strophenboost/
sudo chown -R strophenboost:strophenboost /opt/strophenboost/

# 6. Restart services
sudo supervisorctl restart strophenboost strophenboost-rtmp
sudo systemctl reload nginx
```

### File Transfer Best Practices

1. **Use proper transfer methods:**
   ```bash
   # SCP with proper options
   scp -p update_simple.sh root@your-server:~/
   
   # Or rsync for better reliability
   rsync -avz update_simple.sh root@your-server:~/
   ```

2. **Verify file integrity after transfer:**
   ```bash
   # Check file size matches
   wc -c update_simple.sh
   
   # Test syntax immediately after transfer
   bash -n update_simple.sh
   ```

3. **Fix line endings if needed:**
   ```bash
   # Install dos2unix if needed
   sudo apt install dos2unix
   
   # Convert line endings
   dos2unix update_simple.sh
   ```

### Verification Commands

After any update method:

```bash
# Check service status
sudo supervisorctl status

# Check application logs
sudo tail -f /var/log/strophenboost/app.log

# Test web access
curl -I http://your-domain.com

# Check RTMP server
sudo netstat -tlnp | grep :1935
```

## Available Update Scripts

1. **update_simple.sh** - Ultra-compatible version (recommended for problematic VPS)
2. **update_clean.sh** - Standard version with clean formatting
3. **update.sh** - Original version (may have transfer issues)

Always use `update_simple.sh` if you're experiencing syntax errors on your VPS.