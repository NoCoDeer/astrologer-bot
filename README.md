# 🌟 Astrologer Telegram Bot

A multilingual AI-powered Telegram bot offering comprehensive astrological services including personalized horoscopes, tarot readings, natal chart analysis, and numerology insights.

## ✨ Features

### 🔮 Core Services
- **Personal Horoscopes**: Daily, weekly, and monthly personalized readings
- **Tarot Readings**: Multiple spread types with AI interpretation
- **Natal Chart Analysis**: Complete birth chart calculations and interpretations
- **Numerology**: Life path, expression, soul urge, and personality numbers
- **AI Chat**: Conversational astrological guidance

### 🌍 Multilingual Support
- English (🇬🇧)
- Russian (🇷🇺)
- Spanish (🇪🇸)

### 💎 Subscription System
- **Free Tier**: Limited daily horoscopes and weekly tarot readings
- **Premium**: Unlimited access to all features
- **Payment Integration**: Telegram Payments, Telegram Stars and Yookassa

- **Admin Panel**: HTTP Basic authenticated interface for viewing users and payments

### 🤖 AI Integration
- **Llama 4 Maverick** via OpenRouter for interpretations
- Contextual responses based on user's birth data
- Optimized prompts for astrological accuracy

## 🏗️ Architecture

### Backend Stack
- **Python 3.11+** with FastAPI
- **PostgreSQL** for data persistence
- **Redis** for caching and Celery
- **Celery** for scheduled tasks
- **SQLAlchemy** with async support
- **python-telegram-bot** for Telegram integration

### Services
- **Astrology Service**: Swiss Ephemeris calculations
- **AI Service**: OpenRouter API integration
- **Tarot Service**: Card deck management and spreads
- **Numerology Service**: Pythagorean system calculations

### Infrastructure
- **Docker** containerization
- **Docker Compose** for orchestration
- **Nginx** reverse proxy (production)
- **Celery Beat** for scheduled horoscopes


## Installation

For a complete step-by-step setup guide see [INSTALL.md](INSTALL.md). It explains how to upload the project archive, run the web installer and start the bot using Docker.

## License

This project is released under the MIT License.
