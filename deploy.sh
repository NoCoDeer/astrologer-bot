#!/bin/bash
# Interactive deployment script for Ubuntu 22.04
set -e

REPO_URL=${REPO_URL:-https://github.com/example/astrologer-bot.git}
APP_DIR=${APP_DIR:-/opt/astrologer-bot}

check_root() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "Please run this script as root" >&2
    exit 1
  fi
}

install_docker() {
  if ! command -v docker >/dev/null; then
    apt-get update
    apt-get install -y ca-certificates curl gnupg git openssl
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
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

prompt() {
  local var_name=$1
  local default_value=$2
  local value
  read -p "Enter $var_name${default_value:+ [$default_value]}: " value
  echo "${value:-$default_value}"
}

configure_env() {
  echo "\nConfiguring environment variables..."

  TELEGRAM_BOT_TOKEN=$(prompt "Telegram Bot Token" "")
  OPENROUTER_API_KEY=$(prompt "OpenRouter API Key" "")
  TELEGRAM_WEBHOOK_URL=$(prompt "Telegram Webhook URL" "")
  TELEGRAM_PAYMENTS_TOKEN=$(prompt "Telegram Payments Token" "")
  YOOKASSA_SHOP_ID=$(prompt "Yookassa Shop ID" "")
  YOOKASSA_SECRET_KEY=$(prompt "Yookassa Secret Key" "")
  GEOCODING_API_KEY=$(prompt "Geocoding API Key" "")
  TIMEZONE=$(prompt "Timezone" "UTC")
  AI_MODEL=$(prompt "AI Model" "anthropic/claude-3.5-sonnet")
  POSTGRES_PASSWORD=$(prompt "PostgreSQL password" "$(openssl rand -hex 16)")
  SECRET_KEY=$(openssl rand -hex 32)

  cat > backend/.env <<EENV
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
TELEGRAM_WEBHOOK_URL=$TELEGRAM_WEBHOOK_URL
TELEGRAM_PAYMENTS_TOKEN=$TELEGRAM_PAYMENTS_TOKEN
DATABASE_URL=postgresql+asyncpg://astrologer:${POSTGRES_PASSWORD}@postgres:5432/astrologer_bot
REDIS_URL=redis://redis:6379/0
OPENROUTER_API_KEY=$OPENROUTER_API_KEY
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=$AI_MODEL
YOOKASSA_SHOP_ID=$YOOKASSA_SHOP_ID
YOOKASSA_SECRET_KEY=$YOOKASSA_SECRET_KEY
GEOCODING_API_KEY=$GEOCODING_API_KEY
SECRET_KEY=$SECRET_KEY
TIMEZONE=$TIMEZONE
LOG_LEVEL=INFO
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
STATIC_FILES_PATH=/app/static
CHARTS_PATH=/app/static/charts
TAROT_CARDS_PATH=/app/static/tarot_cards
MONTHLY_SUBSCRIPTION_PRICE=99000
YEARLY_SUBSCRIPTION_PRICE=990000
EENV

  echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" > .env
}

start_services() {
  docker-compose --profile production up --build -d
}

check_root
install_docker
clone_repo
configure_env
start_services
