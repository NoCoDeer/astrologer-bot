from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="en")
    
    # Birth data
    birth_date = Column(DateTime, nullable=True)
    birth_time = Column(String(10), nullable=True)  # HH:MM format
    birth_place = Column(String(255), nullable=True)
    birth_latitude = Column(Float, nullable=True)
    birth_longitude = Column(Float, nullable=True)
    birth_timezone = Column(String(50), nullable=True)
    
    # Preferences
    preferred_horoscope_time = Column(String(10), default="08:00")  # HH:MM format
    timezone = Column(String(50), default="UTC")
    
    # Subscription info
    subscription_type = Column(String(20), default="free")  # free, premium
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    daily_horoscopes_used = Column(Integer, default=0)
    weekly_tarot_readings_used = Column(Integer, default=0)
    last_reset_date = Column(DateTime, default=func.now())
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    horoscopes = relationship("Horoscope", back_populates="user")
    tarot_readings = relationship("TarotReading", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"
    
    @property
    def full_name(self):
        parts = [self.first_name, self.last_name]
        return " ".join(filter(None, parts)) or self.username or f"User {self.telegram_id}"
    
    @property
    def is_premium(self):
        if self.subscription_type == "premium" and self.subscription_expires_at:
            from datetime import datetime
            return datetime.utcnow() < self.subscription_expires_at
        return False
    
    def can_use_feature(self, feature: str) -> bool:
        """Check if user can use a specific feature based on subscription"""
        from src.config import SUBSCRIPTION_TIERS
        
        tier = "premium" if self.is_premium else "free"
        limits = SUBSCRIPTION_TIERS[tier]
        
        if feature == "daily_horoscope":
            return limits["daily_horoscopes"] == -1 or self.daily_horoscopes_used < limits["daily_horoscopes"]
        elif feature == "tarot_reading":
            return limits["tarot_readings_per_week"] == -1 or self.weekly_tarot_readings_used < limits["tarot_readings_per_week"]
        elif feature in ["natal_chart", "numerology", "ai_chat"]:
            return limits.get(feature, False)
        
        return False
    
    def reset_usage_counters(self):
        """Reset daily/weekly usage counters"""
        from datetime import datetime, timedelta
        
        now = datetime.utcnow()
        
        # Reset daily counter if it's a new day
        if self.last_reset_date.date() < now.date():
            self.daily_horoscopes_used = 0
        
        # Reset weekly counter if it's a new week (Monday)
        days_since_monday = now.weekday()
        week_start = now - timedelta(days=days_since_monday)
        if self.last_reset_date < week_start:
            self.weekly_tarot_readings_used = 0
        
        self.last_reset_date = now
