from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database import Base


class TarotReading(Base):
    __tablename__ = "tarot_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Reading details
    reading_type = Column(String(20), nullable=False)  # single, three_card, celtic_cross
    question = Column(Text, nullable=True)  # User's question
    cards_drawn = Column(JSON, nullable=False)  # List of card names and positions
    interpretation = Column(Text, nullable=False)  # AI-generated interpretation
    
    # AI generation details
    ai_model_used = Column(String(100), nullable=True)
    generation_time = Column(DateTime, default=func.now())
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tarot_readings")
    
    def __repr__(self):
        return f"<TarotReading(user_id={self.user_id}, type={self.reading_type}, cards={len(self.cards_drawn)})>"
    
    @property
    def card_names(self):
        """Get list of card names from the cards_drawn JSON"""
        if isinstance(self.cards_drawn, list):
            return [card.get('name', '') for card in self.cards_drawn]
        return []
    
    @property
    def formatted_cards(self):
        """Get formatted string of cards for display"""
        if isinstance(self.cards_drawn, list):
            return ", ".join([card.get('name', '') for card in self.cards_drawn])
        return ""
