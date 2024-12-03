#!/usr/bin/env python3
import os
import subprocess
import sys
import socket
import shutil
def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.decode('utf-8'), error.decode('utf-8')



def setup_venv():
    print("Setting up virtual environment...")
    run_command("python3 -m venv .venv")
    run_command("source .venv/bin/activate")

def clone_repo():
    print("Cloning repository...")
    run_command("git clone https://github.com/amatak-org/kpanel_v1.git")
    run_command("unzip kpanel_v1-main.zip")
    os.chdir("kpanel_v1")
    
def copy_kpanel_functions():
    source = 'kpanel_v1'
    destination = '/var/www/kpanel_v1'
    try:
        shutil.copytree(source, destination)
        return f"Successfully copied {source} to {destination}"
    except Exception as e:
        return f"Error copying folder: {str(e)}"

def generate_nginx_config(site_name):
    config_content = f"""
    server {{
        listen 80;
        server_name {site_name};
        root /var/www/{site_name};
        index index.html index.htm index.nginx-debian.html;

        location / {{
            try_files $uri $uri/ =404;
        }}
    }}
    """
    config_path = f"/etc/nginx/sites-available/{site_name}.conf"
    enabled_path = f"/etc/nginx/sites-enabled/{site_name}.conf"
    
    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        os.symlink(config_path, enabled_path)
        
        run_command("sudo nginx -t")
        run_command("sudo systemctl reload nginx")
        
        return f"Nginx configuration for {site_name} created and enabled."
    except Exception as e:
        return f"Error creating Nginx con"

def install_requirements():
    print("Installing requirements...")
    run_command("pip install -r requirements.txt")

def start_kpanel():
    print("Starting kpanel...")
    run_command("python kpanel.py")

def main():
    setup_venv()
    clone_repo()
    install_requirements()
    start_kpanel()

if __name__ == "__main__":
    main()
