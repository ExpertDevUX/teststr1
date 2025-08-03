# StrophenBoost - Professional Live Streaming Platform

A comprehensive live streaming platform similar to Twitch, built with Python Flask and featuring professional broadcasting capabilities.

## 🚀 Quick Start

### Automated Installation

The installation script works with both regular users and root:

```bash
# Works as regular user with sudo privileges
./install.sh

# Also works as root (creates application user automatically)
sudo ./install.sh
```

The script will automatically:
- Install all system dependencies
- Configure SSL certificates via Let's Encrypt
- Set up PostgreSQL database
- Configure Nginx reverse proxy
- Set up process management
- Create admin user account

## 📋 Prerequisites

### System Requirements
- Ubuntu 20.04+ or Debian 11+
- Minimum 2GB RAM, 2 CPU cores
- 20GB+ storage space
- Domain name with DNS access

### Before Installation
1. **Domain Setup**: Point your domain to your server IP
2. **Cloudflare Account**: For automated SSL certificate setup
3. **API Token**: Create a Cloudflare API token with Zone:Edit permissions
   - Visit: https://dash.cloudflare.com/profile/api-tokens

## 🎯 Features

### 🎥 Professional Streaming
- **RTMP Server**: Compatible with OBS Studio, vMix, XSplit
- **Multi-format Output**: HLS and DASH streaming protocols
- **FFmpeg Integration**: Automatic video transcoding
- **Quality Settings**: Adaptive bitrate streaming

### 💬 Real-time Chat
- **WebSocket-powered**: Instant messaging
- **AI Bot Integration**: Gemini-powered moderation
- **Chat Management**: Admin moderation tools
- **User Roles**: Broadcaster and viewer permissions

### 🎛️ Admin Dashboard
- **User Management**: Complete user administration  
- **Stream Analytics**: Detailed viewing statistics
- **Content Management**: Stream moderation tools
- **System Settings**: Platform configuration

### 🔒 Security & Performance
- **SSL Encryption**: Automatic Let's Encrypt certificates
- **User Authentication**: Secure login system
- **Database Security**: PostgreSQL with proper permissions
- **Firewall Configuration**: UFW security rules

## 🛠️ Manual Setup

For detailed manual installation instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 📖 Usage

### For Streamers
1. **Register Account**: Create your broadcaster account
2. **Get Stream Key**: Generate RTMP key in dashboard
3. **Configure Software**: Use `/streaming/setup` guide
4. **Start Streaming**: Begin broadcasting to your audience

### For Viewers
1. **Browse Streams**: Discover live content
2. **Join Chat**: Participate in real-time discussions
3. **Create Account**: Register for enhanced features

### Streaming Software Configuration

#### OBS Studio
```
Service: Custom
Server: rtmp://yourdomain.com:1935/live
Stream Key: [Your Generated Key]
```

#### vMix
```
Destination: Custom RTMP Server  
URL: rtmp://yourdomain.com:1935/live/[Your_Stream_Key]
```

## 🔧 Administration

### Service Management
```bash
# Check service status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart strophenboost
sudo systemctl restart nginx

# View logs
tail -f /var/log/strophenboost/app.log
```

### SSL Certificate Renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Manual renewal
sudo certbot renew
sudo systemctl reload nginx
```

## 📁 Project Structure

```
strophenboost/
├── app.py                 # Flask application setup
├── main.py               # Application entry point
├── routes.py             # URL routes and handlers
├── models.py             # Database models
├── chat_manager.py       # Real-time chat system
├── rtmp_server.py        # RTMP streaming server
├── ffmpeg_manager.py     # Video processing
├── streaming.py          # Stream management
├── templates/            # HTML templates
├── static/              # CSS, JS, images
├── install.sh           # User installation script
├── install-root.sh      # Root installation script
└── DEPLOYMENT.md        # Detailed deployment guide
```

## 🎨 Customization

### Themes and Styling
- Edit templates in `templates/` directory
- Modify CSS in `static/css/`
- Update JavaScript in `static/js/`

### AI Integration
Add your Gemini API key to `/opt/strophenboost/.env`:
```bash
GEMINI_API_KEY=your_api_key_here
```

### Database Configuration
All database settings are in the `.env` file:
```bash
DATABASE_URL=postgresql://user:pass@localhost/db
```

## 🔍 Troubleshooting

### Common Issues

#### RTMP Connection Problems
1. Check firewall: `sudo ufw status`
2. Verify RTMP server: `sudo supervisorctl status strophenboost-rtmp`
3. Test connectivity: `telnet yourdomain.com 1935`

#### SSL Certificate Issues
1. Verify DNS: `nslookup yourdomain.com`
2. Check Cloudflare token permissions
3. Review certificate logs: `sudo tail -f /var/log/letsencrypt/letsencrypt.log`

#### Performance Optimization
1. Increase Gunicorn workers for high traffic
2. Configure Nginx caching for static content
3. Monitor system resources: `htop`, `iotop`

## 📊 Monitoring

### Log Files
- Application: `/var/log/strophenboost/app.log`
- RTMP Server: `/var/log/strophenboost/rtmp.log`
- Nginx: `/var/log/nginx/access.log`
- PostgreSQL: `/var/log/postgresql/`

### Health Checks
```bash
# Service status
sudo supervisorctl status

# Database connection
sudo -u postgres psql -c "SELECT version();"

# Nginx configuration
sudo nginx -t
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed setup
- **Issues**: Create an issue in the repository
- **Community**: Join our discussion forums

## 🙏 Acknowledgments

- Flask and Python community
- FFmpeg developers
- Video.js team
- Bootstrap contributors
- Let's Encrypt for free SSL certificates

---

**StrophenBoost** - Empowering creators with professional streaming technology.