#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import secrets
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command safely"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return result.stdout.strip()
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def is_root():
    """Check if running as root"""
    return os.geteuid() == 0

def main():
    print("StrophenBoost Python Installer")
    print("=============================")
    
    APP_USER = "strophenboost"
    APP_DIR = "/opt/strophenboost"
    CURRENT_DIR = os.getcwd()
    SUDO = "" if is_root() else "sudo"
    
    # Check if this is new install or update
    if not os.path.exists(APP_DIR):
        print("New Installation")
        domain = input("Enter domain: ").strip()
        email = input("Enter email: ").strip()
        new_install = True
    else:
        print("Update Mode")
        new_install = False
        domain = ""
        email = ""
    
    # Install packages
    print("Installing packages...")
    run_command(f"{SUDO} apt update")
    
    if new_install:
        run_command(f"{SUDO} add-apt-repository -y ppa:deadsnakes/ppa")
        run_command(f"{SUDO} apt update")
        packages = [
            "python3.10", "python3.10-venv", "python3.10-dev", "python3-pip",
            "nginx", "supervisor", "postgresql", "postgresql-contrib", 
            "ffmpeg", "curl", "wget", "git", "ufw", "certbot", "python3-certbot-nginx"
        ]
        run_command(f"{SUDO} apt install -y " + " ".join(packages))
    else:
        run_command(f"{SUDO} apt upgrade -y")
    
    # Setup user and database for new installs
    if new_install:
        print("Setting up user...")
        run_command(f"{SUDO} useradd -r -m -s /bin/bash {APP_USER}", check=False)
        run_command(f"{SUDO} mkdir -p {APP_DIR}")
        run_command(f"{SUDO} chown {APP_USER}:{APP_USER} {APP_DIR}")
        
        print("Setting up database...")
        run_command(f"{SUDO} systemctl start postgresql")
        run_command(f"{SUDO} systemctl enable postgresql")
        run_command(f"{SUDO} -u postgres createuser {APP_USER}", check=False)
        run_command(f"{SUDO} -u postgres createdb -O {APP_USER} strophenboost", check=False)
        run_command(f"{SUDO} -u postgres psql -c \"ALTER USER {APP_USER} PASSWORD 'strophenboost123';\"", check=False)
    
    # Stop services for updates
    if not new_install:
        print("Stopping services...")
        run_command(f"{SUDO} supervisorctl stop strophenboost", check=False)
        run_command(f"{SUDO} supervisorctl stop strophenboost-rtmp", check=False)
        
        # Create backup
        import datetime
        backup_dir = f"/opt/strophenboost-backup-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        run_command(f"{SUDO} cp -r {APP_DIR} {backup_dir}")
        print(f"Backup created: {backup_dir}")
    
    # Copy files
    print("Copying files...")
    files = [
        "app.py", "main.py", "routes.py", "models.py", "chat_manager.py",
        "rtmp_server.py", "ffmpeg_manager.py", "streaming.py", "utils.py",
        "embed.py", "rtmp_utils.py", "start_rtmp_server.py", "pyproject.toml",
        ".replit", "README.md"
    ]
    
    for file in files:
        src = os.path.join(CURRENT_DIR, file)
        if os.path.exists(src):
            dst = os.path.join(APP_DIR, file)
            run_command(f"{SUDO} cp {src} {dst}")
            run_command(f"{SUDO} chown {APP_USER}:{APP_USER} {dst}")
            print(f"Copied {file}")
    
    # Copy directories
    for dir_name in ["templates", "static"]:
        src_dir = os.path.join(CURRENT_DIR, dir_name)
        if os.path.exists(src_dir):
            dst_dir = os.path.join(APP_DIR, dir_name)
            run_command(f"{SUDO} rm -rf {dst_dir}")
            run_command(f"{SUDO} cp -r {src_dir} {dst_dir}")
            run_command(f"{SUDO} chown -R {APP_USER}:{APP_USER} {dst_dir}")
            print(f"Copied {dir_name} directory")
    
    # Create required directories
    run_command(f"{SUDO} mkdir -p {APP_DIR}/stream_output {APP_DIR}/instance")
    run_command(f"{SUDO} chown -R {APP_USER}:{APP_USER} {APP_DIR}/stream_output {APP_DIR}/instance")
    
    # Setup Python environment
    print("Setting up Python...")
    if new_install:
        if is_root():
            run_command(f"su - {APP_USER} -c 'cd {APP_DIR} && python3.10 -m venv venv'")
        else:
            run_command(f"sudo -u {APP_USER} bash -c 'cd {APP_DIR} && python3.10 -m venv venv'")
    
    # Install Python packages
    pip_packages = [
        "flask==2.0.3", "flask-sqlalchemy==2.5.1", "flask-login==0.6.3",
        "flask-socketio==5.3.6", "flask-cors==4.0.0", "flask-wtf==1.1.1",
        "gunicorn==21.2.0", "psycopg2-binary==2.9.7", "email-validator==2.0.0",
        "werkzeug==2.0.3", "sqlalchemy==1.4.53"
    ]
    
    pip_cmd = f"cd {APP_DIR} && source venv/bin/activate && pip install --upgrade pip && pip install " + " ".join(pip_packages)
    
    if is_root():
        run_command(f"su - {APP_USER} -c '{pip_cmd}'")
    else:
        run_command(f"sudo -u {APP_USER} bash -c '{pip_cmd}'")
    
    # Create configuration for new installs
    if new_install:
        print("Creating configuration...")
        secret_key = secrets.token_hex(32)
        
        env_content = f"""DATABASE_URL=postgresql://{APP_USER}:strophenboost123@localhost/strophenboost
SESSION_SECRET={secret_key}"""
        
        if domain:
            env_content += f"\nDOMAIN={domain}"
        
        with open("/tmp/strophenboost.env", "w") as f:
            f.write(env_content)
        
        run_command(f"{SUDO} mv /tmp/strophenboost.env {APP_DIR}/.env")
        run_command(f"{SUDO} chown {APP_USER}:{APP_USER} {APP_DIR}/.env")
        
        # Setup Supervisor
        print("Setting up Supervisor...")
        supervisor_config = f"""[program:strophenboost]
command={APP_DIR}/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 main:app
directory={APP_DIR}
user={APP_USER}
autostart=true
autorestart=true
stdout_logfile=/var/log/strophenboost/app.log
stderr_logfile=/var/log/strophenboost/app.log

[program:strophenboost-rtmp]
command={APP_DIR}/venv/bin/python start_rtmp_server.py
directory={APP_DIR}
user={APP_USER}
autostart=true
autorestart=true
stdout_logfile=/var/log/strophenboost/rtmp.log
stderr_logfile=/var/log/strophenboost/rtmp.log
"""
        
        with open("/tmp/strophenboost.conf", "w") as f:
            f.write(supervisor_config)
        
        run_command(f"{SUDO} mkdir -p /var/log/strophenboost")
        run_command(f"{SUDO} chown {APP_USER}:{APP_USER} /var/log/strophenboost")
        run_command(f"{SUDO} mv /tmp/strophenboost.conf /etc/supervisor/conf.d/")
        
        # Setup Nginx
        if domain:
            print("Setting up Nginx...")
            nginx_config = f"""server {{
    listen 80;
    server_name {domain};
    
    location / {{
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /static {{
        alias {APP_DIR}/static;
        expires 1y;
    }}
    
    location /stream_output {{
        alias {APP_DIR}/stream_output;
        add_header Access-Control-Allow-Origin *;
    }}
}}"""
            
            with open("/tmp/strophenboost.nginx", "w") as f:
                f.write(nginx_config)
            
            run_command(f"{SUDO} mv /tmp/strophenboost.nginx /etc/nginx/sites-available/strophenboost")
            run_command(f"{SUDO} ln -sf /etc/nginx/sites-available/strophenboost /etc/nginx/sites-enabled/")
            run_command(f"{SUDO} rm -f /etc/nginx/sites-enabled/default")
            run_command(f"{SUDO} nginx -t")
            run_command(f"{SUDO} systemctl restart nginx")
    
    # Start services
    print("Starting services...")
    run_command(f"{SUDO} supervisorctl reread")
    run_command(f"{SUDO} supervisorctl update")
    run_command(f"{SUDO} supervisorctl restart strophenboost", check=False)
    run_command(f"{SUDO} supervisorctl restart strophenboost-rtmp", check=False)
    
    if not new_install:
        run_command(f"{SUDO} systemctl reload nginx")
    
    # Setup SSL and firewall for new installs
    if new_install and domain and email:
        print("Setting up SSL...")
        run_command(f"{SUDO} certbot --nginx -d {domain} --email {email} --agree-tos --non-interactive", check=False)
        
        print("Setting up firewall...")
        run_command(f"{SUDO} ufw --force enable")
        run_command(f"{SUDO} ufw allow ssh")
        run_command(f"{SUDO} ufw allow 'Nginx Full'")
        run_command(f"{SUDO} ufw allow 1935/tcp")
    
    # Final message
    print("\n" + "="*40)
    if new_install:
        print("INSTALLATION COMPLETE!")
    else:
        print("UPDATE COMPLETE!")
    print("="*40)
    print("StrophenBoost is ready!")
    print(f"App: {APP_DIR}")
    print("Logs: /var/log/strophenboost/")
    if domain:
        print(f"Web: https://{domain}")
        print(f"RTMP: rtmp://{domain}:1935/live")
    print("Done!")

if __name__ == "__main__":
    main()