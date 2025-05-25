from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database import Base


class Horoscope(Base):
    __tablename__ = "horoscopes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Horoscope details
    horoscope_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    content = Column(Text, nullable=False)
    date_for = Column(DateTime, nullable=False)  # The date this horoscope is for
    
    # AI generation details
    ai_model_used = Column(String(100), nullable=True)
    generation_time = Column(DateTime, default=func.now())
    
    # Delivery status
    is_delivered = Column(Boolean, default=False)
    delivered_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="horoscopes")
    
    def __repr__(self):
        return f"<Horoscope(user_id={self.user_id}, type={self.horoscope_type}, date_for={self.date_for})>"
