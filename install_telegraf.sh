#!/bin/bash
# Simple installer for the Node.js Telegraf bot on a fresh Ubuntu server
set -e

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run this script as root" >&2
  exit 1
fi

apt-get update
apt-get install -y curl git build-essential

# Install Node.js 18
if ! command -v node >/dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
  apt-get install -y nodejs
fi

# Install PM2 process manager
if ! command -v pm2 >/dev/null; then
  npm install -g pm2
fi

REPO_DIR=/opt/astrologer-bot
if [ ! -d "$REPO_DIR" ]; then
  git clone https://github.com/NoCoDeer/astrologer-bot.git "$REPO_DIR"
fi
cd "$REPO_DIR/bot"

npm install --production

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Edit $REPO_DIR/bot/.env and then run pm2 restart astrologer-bot"
fi

pm2 start index.js --name astrologer-bot
pm2 save

