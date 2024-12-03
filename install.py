#!/usr/bin/env python3

import os
import subprocess
import sys

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

def install_requirements():
    print("Installing requirements...")
    run_command("pip3 install -r requirements.txt")

def start_kpanel():
    print("Starting kpanel...")
    run_command("python3 kpanel.py")

def main():
    setup_venv()
    clone_repo()
    install_requirements()
    start_kpanel()

if __name__ == "__main__":
    main()
