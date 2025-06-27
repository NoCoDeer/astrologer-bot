# Installation Guide (Telegraf.js Version)

This guide explains how to deploy **Astrologer Bot** written with [Telegraf.js](https://github.com/telegraf/telegraf) on a fresh Ubuntu server.

## Requirements
- Docker and Docker Compose
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- OpenRouter API key for AI responses

## 1. Clone Repository
```bash
sudo apt update
sudo apt install docker.io docker-compose -y

git clone https://github.com/yourname/astrologer-bot.git
cd astrologer-bot
```

## 2. Configure Environment
Copy the example environment file and edit it with your credentials:
```bash
cp bot/.env.example bot/.env
nano bot/.env
```
Set `TELEGRAM_BOT_TOKEN` and `OPENROUTER_API_KEY`.

## 3. Start Bot
Run the Node.js bot container via Docker Compose:
```bash
docker-compose up node_bot -d
```
The bot will start and connect to Telegram using Telegraf.

## 4. Manage Services
Check running containers and view logs:
```bash
docker-compose ps
docker-compose logs -f node_bot
```
Stop the bot with `docker-compose down`.
