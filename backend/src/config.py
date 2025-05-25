import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Telegram Bot Configuration
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_url: Optional[str] = Field(None, env="TELEGRAM_WEBHOOK_URL")
    telegram_payments_token: Optional[str] = Field(None, env="TELEGRAM_PAYMENTS_TOKEN")
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # AI Configuration
    openrouter_api_key: str = Field(..., env="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field("https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")
    ai_model: str = Field("anthropic/claude-3.5-sonnet", env="AI_MODEL")
    
    # Payment Configuration
    yookassa_shop_id: Optional[str] = Field(None, env="YOOKASSA_SHOP_ID")
    yookassa_secret_key: Optional[str] = Field(None, env="YOOKASSA_SECRET_KEY")
    
    # Geocoding API
    geocoding_api_key: Optional[str] = Field(None, env="GEOCODING_API_KEY")
    
    # Application Configuration
    debug: bool = Field(False, env="DEBUG")
    secret_key: str = Field(..., env="SECRET_KEY")
    timezone: str = Field("UTC", env="TIMEZONE")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Celery Configuration
    celery_broker_url: str = Field("redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field("redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    # File Storage
    static_files_path: str = Field("/app/static", env="STATIC_FILES_PATH")
    charts_path: str = Field("/app/static/charts", env="CHARTS_PATH")
    tarot_cards_path: str = Field("/app/static/tarot_cards", env="TAROT_CARDS_PATH")
    
    # Subscription Pricing (in kopecks for RUB)
    monthly_subscription_price: int = Field(99000, env="MONTHLY_SUBSCRIPTION_PRICE")
    yearly_subscription_price: int = Field(990000, env="YEARLY_SUBSCRIPTION_PRICE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Language configurations
SUPPORTED_LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English", 
    "es": "🇪🇸 Español"
}

DEFAULT_LANGUAGE = "en"

# Tarot deck configuration
TAROT_CARDS = [
    # Major Arcana
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World",
    
    # Minor Arcana - Wands
    "Ace of Wands", "Two of Wands", "Three of Wands", "Four of Wands", "Five of Wands",
    "Six of Wands", "Seven of Wands", "Eight of Wands", "Nine of Wands", "Ten of Wands",
    "Page of Wands", "Knight of Wands", "Queen of Wands", "King of Wands",
    
    # Minor Arcana - Cups
    "Ace of Cups", "Two of Cups", "Three of Cups", "Four of Cups", "Five of Cups",
    "Six of Cups", "Seven of Cups", "Eight of Cups", "Nine of Cups", "Ten of Cups",
    "Page of Cups", "Knight of Cups", "Queen of Cups", "King of Cups",
    
    # Minor Arcana - Swords
    "Ace of Swords", "Two of Swords", "Three of Swords", "Four of Swords", "Five of Swords",
    "Six of Swords", "Seven of Swords", "Eight of Swords", "Nine of Swords", "Ten of Swords",
    "Page of Swords", "Knight of Swords", "Queen of Swords", "King of Swords",
    
    # Minor Arcana - Pentacles
    "Ace of Pentacles", "Two of Pentacles", "Three of Pentacles", "Four of Pentacles", "Five of Pentacles",
    "Six of Pentacles", "Seven of Pentacles", "Eight of Pentacles", "Nine of Pentacles", "Ten of Pentacles",
    "Page of Pentacles", "Knight of Pentacles", "Queen of Pentacles", "King of Pentacles"
]

# Horoscope types
HOROSCOPE_TYPES = {
    "daily": "Daily",
    "weekly": "Weekly", 
    "monthly": "Monthly"
}

# Subscription tiers
SUBSCRIPTION_TIERS = {
    "free": {
        "daily_horoscopes": 1,
        "tarot_readings_per_week": 1,
        "natal_chart": False,
        "numerology": False,
        "ai_chat": False
    },
    "premium": {
        "daily_horoscopes": -1,  # unlimited
        "tarot_readings_per_week": -1,  # unlimited
        "natal_chart": True,
        "numerology": True,
        "ai_chat": True
    }
}
