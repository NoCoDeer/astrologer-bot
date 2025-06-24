from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database import Base


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Payment details
    payment_id = Column(String(255), unique=True, nullable=False)  # External payment ID
    provider = Column(String(50), nullable=False)  # telegram, yookassa
    amount = Column(Float, nullable=False)  # Amount in rubles
    currency = Column(String(10), default="RUB")
    
    # Subscription details
    subscription_type = Column(String(20), nullable=False)  # monthly, yearly
    subscription_months = Column(Integer, nullable=False)  # 1 for monthly, 12 for yearly
    
    # Payment status
    status = Column(String(20), default="pending")  # pending, completed, failed, refunded
    payment_method = Column(String(50), nullable=True)  # card, wallet, etc.
    
    # External references
    telegram_payment_charge_id = Column(String(255), nullable=True)
    yookassa_payment_id = Column(String(255), nullable=True)
    
    # Timestamps
    paid_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # When the subscription expires
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Additional data
    extra_data = Column(Text, nullable=True)  # JSON string for additional data
    
    # Relationships
    user = relationship("User", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(payment_id={self.payment_id}, user_id={self.user_id}, status={self.status})>"
    
    @property
    def is_successful(self):
        return self.status == "completed"
    
    @property
    def is_active_subscription(self):
        """Check if this payment represents an active subscription"""
        if not self.is_successful or not self.expires_at:
            return False
        
        from datetime import datetime
        return datetime.utcnow() < self.expires_at
