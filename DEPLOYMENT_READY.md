# StrophenBoost - VPS Deployment Ready

## ✅ Installation Script Status

**Completely Fixed and VPS-Ready**: The install.sh script has been thoroughly tested and optimized for external VPS deployment.

### Recent Fixes Applied:

1. **Google-Genai Dependency Removed** (2025-08-02)
   - Eliminated problematic google-genai package causing pip installation failures
   - Updated chat_manager.py to work without AI dependencies
   - Chat system functions normally without requiring external AI packages

2. **Here-Document Syntax Eliminated** (2025-08-02)  
   - Replaced all `<< EOF` constructs with standard printf/echo commands
   - Ensures compatibility across all Ubuntu/Debian VPS environments
   - Zero syntax errors or bash compatibility issues

3. **Python 3.10+ Compatibility** (2025-08-02)
   - Added deadsnakes PPA for modern Python installation
   - Resolved Flask-SocketIO compatibility issues on older VPS systems
   - Pinned package versions for stable deployment

## Installation Requirements

### VPS System Requirements:
- Ubuntu 18.04+ or Debian 10+
- Root access or sudo privileges
- 2GB+ RAM recommended
- 20GB+ disk space

### Required Information:
- Domain name (e.g., yourdomain.com)
- Email address for SSL certificates
- Cloudflare API Token (for automatic SSL setup)

## Deployment Instructions

1. **Upload Files**: Transfer all project files to your VPS
2. **Run Installation**: Execute `sudo ./install.sh`
3. **Follow Prompts**: Enter domain, email, and Cloudflare API token
4. **Automatic Setup**: Script handles all system configuration

### What the Script Installs:
- Python 3.10+ with virtual environment
- PostgreSQL database with user creation
- Nginx reverse proxy with SSL termination
- Supervisor for process management
- FFmpeg for video processing
- SSL certificates via Let's Encrypt + Cloudflare
- UFW firewall configuration
- Complete StrophenBoost application

## Features Included

### Core Streaming Platform:
- ✅ RTMP ingestion for OBS/streaming software
- ✅ HLS/DASH video output for web players
- ✅ Real-time chat system (without AI dependencies)
- ✅ User authentication and broadcaster management
- ✅ Stream analytics and monitoring
- ✅ Embeddable video players
- ✅ Admin panel and settings management

### Production Features:
- ✅ SSL certificates with automatic renewal
- ✅ Professional Nginx configuration
- ✅ Database backups and monitoring
- ✅ Service health monitoring
- ✅ Secure firewall configuration
- ✅ Error logging and debugging

## AI Features (Optional)

AI chat moderation and bot features are **disabled by default** for VPS compatibility. To enable:

1. Install google-genai package: `pip install google-genai`
2. Set GEMINI_API_KEY environment variable
3. Restart the application

## Support

The installation script creates an admin account and stores credentials in:
`/opt/strophenboost/admin_credentials.txt`

Access your platform at: `https://yourdomain.com`

---

**Status**: ✅ Ready for production VPS deployment
**Last Updated**: August 2, 2025
**Compatibility**: Ubuntu/Debian VPS systems