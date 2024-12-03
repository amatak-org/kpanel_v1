#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function copyFolder() {
  const sourceFolder = 'kpanel_v1';
  const destinationFolder = '/var/www/kpanel_v1/';

  execSync(`sudo cp -r ${sourceFolder} ${destinationFolder}`);
}

function installNginx() {
  execSync('sudo apt update');
  execSync('sudo apt install nginx -y');
}

function configureNginx() {
  const configContent = `
server {
    listen 80;
    server_name kpanel.config;
    root /var/www/kpanel_v1/;
    index index.html index.htm;

    location / {
        try_files $uri $uri/ =404;
    }
}
`;

  fs.writeFileSync('/etc/nginx/sites-available/kpanel.config', configContent);
  execSync('sudo ln -s /etc/nginx/sites-available/kpanel.config /etc/nginx/sites-enabled/');
  execSync('sudo nginx -t');
  execSync('sudo systemctl restart nginx');
}

function install() {
  copyFolder();
  installNginx();
  configureNginx();
  console.log('Installation completed successfully.');
}

if (process.argv[2] === 'install') {
  install();
} else {
  console.log('Usage: node script.js install');
}
