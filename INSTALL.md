# Installation Guide

This guide describes how to quickly deploy **Astrologer Bot** on any Ubuntu server.

## Requirements
- Docker and Docker Compose
- Python 3.11+ with `pip`

## 1. Upload and Unpack
1. Download the latest release archive of the project.
2. Upload the archive to your server and unzip it:
   ```bash
   unzip astrologer-bot.zip
   cd astrologer-bot
   ```

## 2. Install Prerequisites
Install Docker and Python packages if they are not present:
```bash
sudo apt update
sudo apt install docker.io docker-compose python3 python3-pip -y
```

## 3. Run the Web Installer
Install the small web installer and start it:
```bash
pip3 install -r installer/requirements.txt
python3 installer/app.py
```
Open `http://<your-server-ip>:8080` in a browser. Fill in the form with your Telegram tokens, API keys and desired admin credentials. After submission the installer writes the configuration and launches all Docker containers.

## 4. Finish
Once installation completes the bot will be running. Access the admin panel with the credentials you provided. To manage the bot later, use standard Docker Compose commands:
```bash
docker-compose ps       # check services
docker-compose logs -f  # view logs
```
