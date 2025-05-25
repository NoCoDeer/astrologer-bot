import random
from typing import Dict, List, Any, Optional
from src.config import TAROT_CARDS
import logging

logger = logging.getLogger(__name__)


class TarotService:
    def __init__(self):
        self.deck = TAROT_CARDS.copy()
        
        # Tarot spread configurations
        self.spreads = {
            "single": {
                "name": "Single Card",
                "positions": ["Present Situation"],
                "card_count": 1
            },
            "three_card": {
                "name": "Three Card Spread",
                "positions": ["Past", "Present", "Future"],
                "card_count": 3
            },
            "relationship": {
                "name": "Relationship Spread",
                "positions": ["You", "Your Partner", "The Relationship"],
                "card_count": 3
            },
            "career": {
                "name": "Career Spread", 
                "positions": ["Current Situation", "Challenges", "Advice"],
                "card_count": 3
            },
            "celtic_cross": {
                "name": "Celtic Cross",
                "positions": [
                    "Present Situation",
                    "Challenge/Cross",
                    "Distant Past/Foundation",
                    "Recent Past",
                    "Possible Outcome",
                    "Immediate Future",
                    "Your Approach",
                    "External Influences",
                    "Hopes and Fears",
                    "Final Outcome"
                ],
                "card_count": 10
            }
        }
    
    def shuffle_deck(self) -> List[str]:
        """Shuffle the tarot deck"""
        shuffled = self.deck.copy()
        random.shuffle(shuffled)
        return shuffled
    
    def draw_cards(self, count: int) -> List[Dict[str, Any]]:
        """Draw specified number of cards from shuffled deck"""
        try:
            shuffled_deck = self.shuffle_deck()
            drawn_cards = shuffled_deck[:count]
            
            cards = []
            for i, card_name in enumerate(drawn_cards):
                # Randomly determine if card is reversed (30% chance)
                is_reversed = random.random() < 0.3
                
                cards.append({
                    "name": card_name,
                    "position_index": i,
                    "is_reversed": is_reversed,
                    "display_name": f"{card_name} (Reversed)" if is_reversed else card_name
                })
            
            return cards
            
        except Exception as e:
            logger.error(f"Card drawing error: {e}")
            raise
    
    def create_reading(
        self, 
        spread_type: str, 
        question: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a complete tarot reading"""
        try:
            if spread_type not in self.spreads:
                raise ValueError(f"Unknown spread type: {spread_type}")
            
            spread_config = self.spreads[spread_type]
            cards = self.draw_cards(spread_config["card_count"])
            
            # Assign positions to cards
            for i, card in enumerate(cards):
                if i < len(spread_config["positions"]):
                    card["position"] = spread_config["positions"][i]
                else:
                    card["position"] = f"Position {i + 1}"
            
            reading = {
                "spread_type": spread_type,
                "spread_name": spread_config["name"],
                "question": question,
                "cards": cards,
                "positions": spread_config["positions"],
                "card_count": len(cards)
            }
            
            return reading
            
        except Exception as e:
            logger.error(f"Reading creation error: {e}")
            raise
    
    def get_card_meaning(self, card_name: str, is_reversed: bool = False) -> Dict[str, str]:
        """Get basic meaning for a tarot card"""
        # Basic card meanings (simplified for demo)
        card_meanings = {
            # Major Arcana
            "The Fool": {
                "upright": "New beginnings, innocence, spontaneity, free spirit",
                "reversed": "Recklessness, taken advantage of, inconsideration"
            },
            "The Magician": {
                "upright": "Manifestation, resourcefulness, power, inspired action",
                "reversed": "Manipulation, poor planning, untapped talents"
            },
            "The High Priestess": {
                "upright": "Intuition, sacred knowledge, divine feminine, subconscious mind",
                "reversed": "Secrets, disconnected from intuition, withdrawal"
            },
            "The Empress": {
                "upright": "Femininity, beauty, nature, nurturing, abundance",
                "reversed": "Creative block, dependence on others"
            },
            "The Emperor": {
                "upright": "Authority, establishment, structure, father figure",
                "reversed": "Domination, excessive control, lack of discipline"
            },
            "The Hierophant": {
                "upright": "Spiritual wisdom, religious beliefs, conformity, tradition",
                "reversed": "Personal beliefs, freedom, challenging the status quo"
            },
            "The Lovers": {
                "upright": "Love, harmony, relationships, values alignment",
                "reversed": "Self-love, disharmony, imbalance, misalignment"
            },
            "The Chariot": {
                "upright": "Control, willpower, success, determination",
                "reversed": "Self-discipline, opposition, lack of direction"
            },
            "Strength": {
                "upright": "Strength, courage, persuasion, influence, compassion",
                "reversed": "Self doubt, low energy, raw emotion"
            },
            "The Hermit": {
                "upright": "Soul searching, introspection, inner guidance",
                "reversed": "Isolation, loneliness, withdrawal"
            },
            "Wheel of Fortune": {
                "upright": "Good luck, karma, life cycles, destiny, turning point",
                "reversed": "Bad luck, lack of control, clinging to control"
            },
            "Justice": {
                "upright": "Justice, fairness, truth, cause and effect, law",
                "reversed": "Unfairness, lack of accountability, dishonesty"
            },
            "The Hanged Man": {
                "upright": "Suspension, restriction, letting go, sacrifice",
                "reversed": "Martyrdom, indecision, delay"
            },
            "Death": {
                "upright": "Endings, beginnings, change, transformation, transition",
                "reversed": "Resistance to change, personal transformation, inner purging"
            },
            "Temperance": {
                "upright": "Balance, moderation, patience, purpose",
                "reversed": "Imbalance, excess, self-healing, re-alignment"
            },
            "The Devil": {
                "upright": "Bondage, addiction, sexuality, materialism",
                "reversed": "Releasing limiting beliefs, exploring dark thoughts, detachment"
            },
            "The Tower": {
                "upright": "Sudden change, upheaval, chaos, revelation, awakening",
                "reversed": "Personal transformation, fear of change, averting disaster"
            },
            "The Star": {
                "upright": "Hope, faith, purpose, renewal, spirituality",
                "reversed": "Lack of faith, despair, self-trust, disconnection"
            },
            "The Moon": {
                "upright": "Illusion, fear, anxiety, subconscious, intuition",
                "reversed": "Release of fear, repressed emotion, inner confusion"
            },
            "The Sun": {
                "upright": "Positivity, fun, warmth, success, vitality",
                "reversed": "Inner child, feeling down, overly optimistic"
            },
            "Judgement": {
                "upright": "Judgement, rebirth, inner calling, absolution",
                "reversed": "Self-doubt, inner critic, ignoring the call"
            },
            "The World": {
                "upright": "Completion, integration, accomplishment, travel",
                "reversed": "Seeking personal closure, short-cut to success"
            }
        }
        
        # Default meaning for cards not in dictionary
        default_meaning = {
            "upright": "Positive energy, growth, opportunity",
            "reversed": "Blocked energy, internal challenges, reflection needed"
        }
        
        meaning = card_meanings.get(card_name, default_meaning)
        return {
            "card": card_name,
            "meaning": meaning["reversed"] if is_reversed else meaning["upright"],
            "orientation": "reversed" if is_reversed else "upright"
        }
    
    def get_spread_description(self, spread_type: str) -> str:
        """Get description of a tarot spread"""
        descriptions = {
            "single": "A single card draw for quick insight into your current situation or a specific question.",
            "three_card": "A classic three-card spread exploring the past, present, and future influences on your situation.",
            "relationship": "A three-card spread focused on relationship dynamics, exploring you, your partner, and the relationship itself.",
            "career": "A three-card spread for career guidance, examining your current situation, challenges, and advice for moving forward.",
            "celtic_cross": "The most comprehensive spread, providing deep insight into all aspects of your situation with 10 cards representing different influences and outcomes."
        }
        
        return descriptions.get(spread_type, "A tarot spread for gaining insight and guidance.")
    
    def format_reading_for_display(self, reading: Dict[str, Any]) -> str:
        """Format a reading for text display"""
        try:
            lines = []
            lines.append(f"🔮 {reading['spread_name']}")
            
            if reading.get('question'):
                lines.append(f"❓ Question: {reading['question']}")
            
            lines.append("")
            lines.append("🃏 Cards drawn:")
            
            for card in reading['cards']:
                position = card.get('position', 'Unknown')
                display_name = card.get('display_name', card['name'])
                lines.append(f"• {position}: {display_name}")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Reading formatting error: {e}")
            return "Error formatting reading"
    
    def get_available_spreads(self) -> Dict[str, Dict[str, Any]]:
        """Get all available tarot spreads with descriptions"""
        spreads_info = {}
        for spread_type, config in self.spreads.items():
            spreads_info[spread_type] = {
                "name": config["name"],
                "card_count": config["card_count"],
                "description": self.get_spread_description(spread_type),
                "positions": config["positions"]
            }
        
        return spreads_info


# Global tarot service instance
tarot_service = TarotService()
