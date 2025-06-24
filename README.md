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
- **Payment Integration**: Telegram Payments + Yookassa

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

## 🚀 Quick Start

### Prerequisites
- Ubuntu 22.04 server
- Telegram Bot Token (from @BotFather)
- OpenRouter API Key
- Optional: domain name and SSL certificates

### 1. Automated Deployment
Run the interactive deployment script on a fresh server to install Docker, configure environment variables and start the bot:
```bash
curl -L https://raw.githubusercontent.com/example/astrologer-bot/main/deploy.sh | sudo bash
```

The script clones the repository into `/opt/astrologer-bot`, asks for all required settings and launches the production services.

### 2. Manual Setup
```bash
git clone <repository-url>
cd astrologer-bot
cp backend/.env.example backend/.env
# edit configuration
nano backend/.env
```

### 3. Configure Environment Variables
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/webhook

# OpenRouter AI
OPENROUTER_API_KEY=your_openrouter_key_here
AI_MODEL=anthropic/claude-3.5-sonnet

# Database
DATABASE_URL=postgresql+asyncpg://astrologer:password@postgres:5432/astrologer_bot

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# Payment (Optional)
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
TELEGRAM_PAYMENT_TOKEN=your_payment_token

# External APIs
GEOCODING_API_KEY=your_geocoding_key
```

### 4. Start Services
```bash
# Development mode
docker-compose up -d

# Production mode with Nginx
docker-compose --profile production up -d

# With monitoring (Flower)
docker-compose --profile monitoring up -d
```

### 5. Verify Installation
```bash
# Check service health
curl http://localhost:8000/health

# View logs
docker-compose logs -f app

# Monitor Celery tasks (if monitoring profile enabled)
open http://localhost:5555
```

### Admin Panel
The React based admin panel is available on port **3000** once the services are running.
It provides:
- 📈 Dashboard with key statistics
- 👥 User management
- 💰 Subscription and tariff control
- 📝 Content management
- 💳 Transaction history
- ⏰ Schedule settings
- ⚙️ Bot configuration
- 📋 Log viewer

To modify the panel UI, edit the files under `frontend/src` and rebuild the container:
```bash
docker-compose build admin
docker-compose up -d admin
```

## 📱 Bot Commands

### User Commands
- `/start` - Initialize bot and setup profile
- `/horoscope` - Get daily horoscope
- `/tarot` - Request tarot reading
- `/natal` - View natal chart analysis
- `/numerology` - Get numerology insights
- `/subscribe` - Upgrade to premium
- `/settings` - Change preferences
- `/profile` - View profile information
- `/help` - Show help information

### Bot Features
- **Onboarding Flow**: Language selection, birth data collection
- **Interactive Menus**: Inline keyboards for navigation
- **Scheduled Delivery**: Daily horoscopes at preferred time
- **Usage Tracking**: Free tier limitations
- **Multi-language**: Automatic localization

## 🔧 Development

### Local Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
export PYTHONPATH=backend
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost/astrologer_bot

# Run database migrations
cd backend
python -c "from src.database import Base, async_engine; import asyncio; asyncio.run(Base.metadata.create_all(async_engine))"

# Start development server
python src/main.py
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest backend/tests/ -v --cov=src
```

### Code Quality
```bash
# Format code
black backend/src/
isort backend/src/

# Lint code
flake8 backend/src/
mypy backend/src/
```

## 🐳 Docker Commands

### Basic Operations
```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f [service_name]

# Execute commands in container
docker-compose exec app python -c "print('Hello')"

# Scale workers
docker-compose up --scale celery_worker=3 -d

# Stop services
docker-compose down

# Clean up (removes volumes)
docker-compose down -v
```

### Database Operations
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U astrologer -d astrologer_bot

# Backup database
docker-compose exec postgres pg_dump -U astrologer astrologer_bot > backup.sql

# Restore database
docker-compose exec -T postgres psql -U astrologer astrologer_bot < backup.sql
```

## 📊 Monitoring

### Application Monitoring
- **Health Endpoint**: `GET /health`
- **Metrics**: Built-in FastAPI metrics
- **Logs**: Structured logging with timestamps

### Celery Monitoring
```bash
# Enable Flower monitoring
docker-compose --profile monitoring up -d

# Access Flower dashboard
open http://localhost:5555
```

### Database Monitoring
```bash
# Check database connections
docker-compose exec postgres psql -U astrologer -d astrologer_bot -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor table sizes
docker-compose exec postgres psql -U astrologer -d astrologer_bot -c "SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size FROM pg_tables WHERE schemaname='public';"
```

## 🚀 Deployment

### Production Deployment
1. **Server Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **SSL Setup** (Optional)
   ```bash
   # Create SSL directory
   mkdir -p nginx/ssl
   
   # Generate self-signed certificate (for testing)
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout nginx/ssl/private.key \
     -out nginx/ssl/certificate.crt
   ```

3. **Production Configuration**
   ```bash
   # Set production environment
   export ENVIRONMENT=production
   
   # Start with production profile
   docker-compose --profile production up -d
   ```

### Environment-Specific Configurations

#### Development
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  app:
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
```

#### Production
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app:
    environment:
      - DEBUG=false
      - LOG_LEVEL=info
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

## 🔐 Security

### Best Practices
- Store sensitive data in environment variables
- Use strong passwords for database
- Enable SSL/TLS in production
- Regularly update dependencies
- Monitor for security vulnerabilities

### API Keys Security
```bash
# Generate secure random keys
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale web application
docker-compose up --scale app=3 -d

# Scale Celery workers
docker-compose up --scale celery_worker=5 -d
```

### Performance Optimization
- Use Redis for caching frequent queries
- Implement database connection pooling
- Optimize AI API calls with batching
- Use CDN for static files

## 🐛 Troubleshooting

### Common Issues

#### Bot Not Responding
```bash
# Check bot logs
docker-compose logs -f app

# Verify bot token
curl https://api.telegram.org/bot<TOKEN>/getMe

# Check webhook status
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U astrologer

# View database logs
docker-compose logs postgres

# Test connection
docker-compose exec app python -c "from src.database import async_engine; print('DB OK')"
```

#### Celery Tasks Not Running
```bash
# Check Celery worker status
docker-compose logs celery_worker

# Check Redis connection
docker-compose exec redis redis-cli ping

# Monitor task queue
docker-compose exec app celery -A src.celery_app inspect active
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=debug

# Run with debug
docker-compose up --build
```

## 📚 API Documentation

### FastAPI Docs
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Webhook Endpoint
```bash
# Set webhook
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourdomain.com/webhook"}'
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Use type hints
- Add docstrings to functions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Swiss Ephemeris** for astronomical calculations
- **OpenRouter** for AI model access
- **python-telegram-bot** for Telegram integration
- **FastAPI** for the web framework
- **Celery** for task scheduling

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details

---

**Made with ❤️ for astrology enthusiasts worldwide** 🌟
