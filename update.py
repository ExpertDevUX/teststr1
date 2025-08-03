#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import datetime
from pathlib import Path

def run_command(cmd, shell=True, check=True):
    """Run a system command safely"""
    try:
        result = subprocess.run(cmd, shell=shell, check=check, capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False

def print_status(message):
    print(f"[INFO] {message}")

def print_success(message):
    print(f"[SUCCESS] {message}")

def print_error(message):
    print(f"[ERROR] {message}")

def is_root():
    return os.geteuid() == 0

def main():
    print("StrophenBoost Update Script")
    print("=" * 50)
    
    # Configuration
    app_user = "strophenboost"
    app_dir = "/opt/strophenboost"
    backup_dir = f"/opt/strophenboost-backup-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    current_dir = os.getcwd()
    
    # Check if installation exists
    print_status("Checking existing installation...")
    if not os.path.exists(app_dir):
        print_error(f"Installation not found at {app_dir}")
        sys.exit(1)
    
    if not os.path.exists(f"{app_dir}/.env"):
        print_error("Configuration file not found")
        sys.exit(1)
    
    print_success("Installation found")
    
    # Stop services
    print_status("Stopping services...")
    if is_root():
        run_command("supervisorctl stop strophenboost", check=False)
        run_command("supervisorctl stop strophenboost-rtmp", check=False)
    else:
        run_command("sudo supervisorctl stop strophenboost", check=False)
        run_command("sudo supervisorctl stop strophenboost-rtmp", check=False)
    
    print_success("Services stopped")
    
    # Create backup
    print_status("Creating backup...")
    try:
        if is_root():
            shutil.copytree(app_dir, backup_dir)
        else:
            run_command(f"sudo cp -r {app_dir} {backup_dir}")
        print_success(f"Backup created at {backup_dir}")
    except Exception as e:
        print_error(f"Backup failed: {e}")
        sys.exit(1)
    
    # Update system packages
    print_status("Updating system packages...")
    if is_root():
        run_command("apt update && apt upgrade -y")
    else:
        run_command("sudo apt update && sudo apt upgrade -y")
    print_success("System packages updated")
    
    # Update Python packages
    print_status("Updating Python packages...")
    packages = [
        "flask==2.0.3",
        "flask-sqlalchemy==2.5.1", 
        "flask-login==0.6.3",
        "flask-socketio==5.3.6",
        "flask-cors==4.0.0",
        "flask-wtf==1.1.1",
        "gunicorn==21.2.0",
        "psycopg2-binary==2.9.7",
        "email-validator==2.0.0",
        "werkzeug==2.0.3",
        "sqlalchemy==1.4.53"
    ]
    
    packages_str = " ".join(packages)
    pip_cmd = f"source venv/bin/activate && pip install --upgrade {packages_str}"
    
    if is_root():
        run_command(f"cd {app_dir} && sudo -u {app_user} bash -c '{pip_cmd}'")
    else:
        run_command(f"cd {app_dir} && bash -c '{pip_cmd}'")
    
    print_success("Python packages updated")
    
    # Update application files
    print_status("Updating application files...")
    
    # Python files to copy
    python_files = [
        "app.py", "main.py", "routes.py", "models.py", "chat_manager.py",
        "rtmp_server.py", "ffmpeg_manager.py", "streaming.py", "utils.py",
        "embed.py", "rtmp_utils.py", "start_rtmp_server.py"
    ]
    
    # Config files to copy
    config_files = ["pyproject.toml", ".replit", "README.md", "DEPLOYMENT.md"]
    
    # Copy individual files
    for file_name in python_files + config_files:
        source_file = os.path.join(current_dir, file_name)
        if os.path.exists(source_file):
            dest_file = os.path.join(app_dir, file_name)
            try:
                if is_root():
                    shutil.copy2(source_file, dest_file)
                    shutil.chown(dest_file, user=app_user, group=app_user)
                else:
                    run_command(f"sudo cp {source_file} {dest_file}")
                    run_command(f"sudo chown {app_user}:{app_user} {dest_file}")
                print_status(f"Updated {file_name}")
            except Exception as e:
                print_error(f"Failed to copy {file_name}: {e}")
    
    # Copy directories
    for dir_name in ["templates", "static"]:
        source_dir = os.path.join(current_dir, dir_name)
        if os.path.exists(source_dir):
            dest_dir = os.path.join(app_dir, dir_name)
            try:
                if os.path.exists(dest_dir):
                    if is_root():
                        shutil.rmtree(dest_dir)
                    else:
                        run_command(f"sudo rm -rf {dest_dir}")
                
                if is_root():
                    shutil.copytree(source_dir, dest_dir)
                    shutil.chown(dest_dir, user=app_user, group=app_user)
                    for root, dirs, files in os.walk(dest_dir):
                        for d in dirs:
                            shutil.chown(os.path.join(root, d), user=app_user, group=app_user)
                        for f in files:
                            shutil.chown(os.path.join(root, f), user=app_user, group=app_user)
                else:
                    run_command(f"sudo cp -r {source_dir} {dest_dir}")
                    run_command(f"sudo chown -R {app_user}:{app_user} {dest_dir}")
                
                print_status(f"Updated {dir_name} directory")
            except Exception as e:
                print_error(f"Failed to copy {dir_name}: {e}")
    
    print_success("Application files updated")
    
    # Restart services
    print_status("Restarting services...")
    if is_root():
        run_command("supervisorctl reread")
        run_command("supervisorctl update")
        run_command("supervisorctl restart strophenboost")
        run_command("supervisorctl restart strophenboost-rtmp")
        run_command("systemctl reload nginx")
    else:
        run_command("sudo supervisorctl reread")
        run_command("sudo supervisorctl update")
        run_command("sudo supervisorctl restart strophenboost")
        run_command("sudo supervisorctl restart strophenboost-rtmp")
        run_command("sudo systemctl reload nginx")
    
    # Wait for services to start
    import time
    time.sleep(5)
    print_success("Services restarted")
    
    # Show completion message
    print()
    print("=" * 60)
    print("                UPDATE COMPLETE!")
    print("=" * 60)
    print()
    print_success("StrophenBoost has been successfully updated!")
    print()
    print(f"Backup Location: {backup_dir}")
    print(f"Application Directory: {app_dir}")
    print()
    print_success("Your streaming platform is ready to use!")

if __name__ == "__main__":
    main()