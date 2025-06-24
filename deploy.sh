#!/bin/bash
# Automated deployment script for Ubuntu 22.04
set -e

REPO_URL=${REPO_URL:-https://github.com/example/astrologer-bot.git}
APP_DIR=${APP_DIR:-/opt/astrologer-bot}

install_docker() {
  if ! command -v docker >/dev/null; then
    apt-get update
    apt-get install -y ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" > /etc/apt/sources.list.d/docker.list
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
  fi

  if ! command -v docker-compose >/dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
  fi
}

clone_repo() {
  if [ ! -d "$APP_DIR" ]; then
    git clone "$REPO_URL" "$APP_DIR"
  fi
  cd "$APP_DIR"
}

prepare_env() {
  if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "Please edit backend/.env before running services"
  fi
}

start_services() {
  docker-compose up --build -d
}

install_docker
clone_repo
prepare_env
start_services
