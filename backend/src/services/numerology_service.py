from datetime import datetime
from typing import Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class NumerologyService:
    def __init__(self):
        # Letter to number mapping for Pythagorean system
        self.letter_values = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
            'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
            'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
        }
        
        # Master numbers that are not reduced
        self.master_numbers = {11, 22, 33}
    
    def reduce_to_single_digit(self, number: int) -> int:
        """Reduce a number to single digit, preserving master numbers"""
        while number > 9 and number not in self.master_numbers:
            number = sum(int(digit) for digit in str(number))
        return number
    
    def calculate_life_path_number(self, birth_date: datetime) -> int:
        """Calculate Life Path Number from birth date"""
        try:
            # Sum all digits in the birth date
            date_str = birth_date.strftime("%m%d%Y")
            total = sum(int(digit) for digit in date_str)
            return self.reduce_to_single_digit(total)
        except Exception as e:
            logger.error(f"Life path calculation error: {e}")
            return 1
    
    def calculate_expression_number(self, full_name: str) -> int:
        """Calculate Expression Number (Destiny Number) from full name"""
        try:
            # Remove non-alphabetic characters and convert to uppercase
            clean_name = re.sub(r'[^A-Za-z]', '', full_name.upper())
            
            total = 0
            for letter in clean_name:
                if letter in self.letter_values:
                    total += self.letter_values[letter]
            
            return self.reduce_to_single_digit(total)
        except Exception as e:
            logger.error(f"Expression number calculation error: {e}")
            return 1
    
    def calculate_soul_urge_number(self, full_name: str) -> int:
        """Calculate Soul Urge Number from vowels in full name"""
        try:
            vowels = 'AEIOU'
            clean_name = re.sub(r'[^A-Za-z]', '', full_name.upper())
            
            total = 0
            for letter in clean_name:
                if letter in vowels and letter in self.letter_values:
                    total += self.letter_values[letter]
            
            return self.reduce_to_single_digit(total)
        except Exception as e:
            logger.error(f"Soul urge calculation error: {e}")
            return 1
    
    def calculate_personality_number(self, full_name: str) -> int:
        """Calculate Personality Number from consonants in full name"""
        try:
            vowels = 'AEIOU'
            clean_name = re.sub(r'[^A-Za-z]', '', full_name.upper())
            
            total = 0
            for letter in clean_name:
                if letter not in vowels and letter in self.letter_values:
                    total += self.letter_values[letter]
            
            return self.reduce_to_single_digit(total)
        except Exception as e:
            logger.error(f"Personality number calculation error: {e}")
            return 1
    
    def calculate_birth_day_number(self, birth_date: datetime) -> int:
        """Calculate Birth Day Number from day of birth"""
        try:
            day = birth_date.day
            return self.reduce_to_single_digit(day)
        except Exception as e:
            logger.error(f"Birth day calculation error: {e}")
            return 1
    
    def calculate_attitude_number(self, birth_date: datetime) -> int:
        """Calculate Attitude Number from birth month and day"""
        try:
            month_day = int(f"{birth_date.month:02d}{birth_date.day:02d}")
            total = sum(int(digit) for digit in str(month_day))
            return self.reduce_to_single_digit(total)
        except Exception as e:
            logger.error(f"Attitude number calculation error: {e}")
            return 1
    
    def calculate_all_numbers(self, full_name: str, birth_date: datetime) -> Dict[str, int]:
        """Calculate all numerology numbers for a person"""
        try:
            return {
                "life_path": self.calculate_life_path_number(birth_date),
                "expression": self.calculate_expression_number(full_name),
                "soul_urge": self.calculate_soul_urge_number(full_name),
                "personality": self.calculate_personality_number(full_name),
                "birth_day": self.calculate_birth_day_number(birth_date),
                "attitude": self.calculate_attitude_number(birth_date)
            }
        except Exception as e:
            logger.error(f"Numerology calculation error: {e}")
            return {}
    
    def get_number_meaning(self, number: int, number_type: str) -> str:
        """Get meaning for a specific numerology number"""
        meanings = {
            "life_path": {
                1: "The Leader - Independent, pioneering, ambitious, and strong-willed. Natural born leaders who are innovative and original.",
                2: "The Peacemaker - Cooperative, diplomatic, sensitive, and patient. Excellent mediators who work well with others.",
                3: "The Creative - Artistic, expressive, optimistic, and inspiring. Natural entertainers with great communication skills.",
                4: "The Builder - Practical, hardworking, reliable, and organized. Excellent at creating solid foundations and systems.",
                5: "The Freedom Seeker - Adventurous, versatile, curious, and progressive. Love variety and freedom in all aspects of life.",
                6: "The Nurturer - Caring, responsible, protective, and healing. Natural caregivers who put family and community first.",
                7: "The Seeker - Analytical, introspective, spiritual, and mysterious. Deep thinkers who seek truth and understanding.",
                8: "The Achiever - Ambitious, material-focused, powerful, and business-minded. Natural ability to achieve material success.",
                9: "The Humanitarian - Compassionate, generous, idealistic, and romantic. Dedicated to serving humanity and making the world better.",
                11: "The Intuitive - Highly intuitive, spiritual, inspirational, and visionary. Master number with great potential for enlightenment.",
                22: "The Master Builder - Practical visionary, capable of turning dreams into reality. Master number with great potential for achievement.",
                33: "The Master Teacher - Highly evolved spiritual teacher, healer, and guide. Master number dedicated to uplifting humanity."
            },
            "expression": {
                1: "Destined to be a leader and pioneer. Your purpose is to initiate new projects and lead others toward success.",
                2: "Destined to be a peacemaker and diplomat. Your purpose is to bring harmony and cooperation to relationships.",
                3: "Destined to be a creative communicator. Your purpose is to inspire and entertain others through artistic expression.",
                4: "Destined to be a builder and organizer. Your purpose is to create stable foundations and practical solutions.",
                5: "Destined to be an adventurer and freedom fighter. Your purpose is to experience life fully and inspire change.",
                6: "Destined to be a nurturer and healer. Your purpose is to care for others and create harmonious environments.",
                7: "Destined to be a seeker of truth. Your purpose is to develop wisdom and share spiritual insights.",
                8: "Destined to achieve material success. Your purpose is to master the material world and achieve recognition.",
                9: "Destined to serve humanity. Your purpose is to be a humanitarian and make the world a better place.",
                11: "Destined to be a spiritual messenger. Your purpose is to inspire and enlighten others through intuitive wisdom.",
                22: "Destined to be a master builder. Your purpose is to create something of lasting value for humanity.",
                33: "Destined to be a master teacher. Your purpose is to heal and uplift humanity through compassionate service."
            },
            "soul_urge": {
                1: "Deep desire for independence and leadership. You want to be first and make your own decisions.",
                2: "Deep desire for peace and cooperation. You want harmony in relationships and to work with others.",
                3: "Deep desire for creative self-expression. You want to communicate, create, and inspire others.",
                4: "Deep desire for security and order. You want stability, organization, and practical achievements.",
                5: "Deep desire for freedom and adventure. You want variety, travel, and new experiences.",
                6: "Deep desire to nurture and heal. You want to care for others and create beautiful, harmonious environments.",
                7: "Deep desire for knowledge and understanding. You want to discover truth and develop spiritual wisdom.",
                8: "Deep desire for material success and recognition. You want to achieve power and financial security.",
                9: "Deep desire to serve humanity. You want to make a difference in the world and help others.",
                11: "Deep desire for spiritual enlightenment. You want to inspire others and serve as a spiritual guide.",
                22: "Deep desire to build something meaningful. You want to create lasting achievements that benefit humanity.",
                33: "Deep desire to heal and teach. You want to serve as a compassionate guide and healer for others."
            },
            "personality": {
                1: "Others see you as confident, independent, and strong. You appear to be a natural leader.",
                2: "Others see you as gentle, cooperative, and diplomatic. You appear to be a peacemaker.",
                3: "Others see you as creative, charming, and entertaining. You appear to be artistic and expressive.",
                4: "Others see you as reliable, practical, and hardworking. You appear to be stable and trustworthy.",
                5: "Others see you as adventurous, versatile, and exciting. You appear to be dynamic and progressive.",
                6: "Others see you as caring, responsible, and nurturing. You appear to be a natural caregiver.",
                7: "Others see you as mysterious, analytical, and wise. You appear to be deep and spiritual.",
                8: "Others see you as successful, ambitious, and powerful. You appear to be business-minded and authoritative.",
                9: "Others see you as compassionate, generous, and idealistic. You appear to be humanitarian and wise.",
                11: "Others see you as intuitive, inspiring, and spiritual. You appear to be a visionary and guide.",
                22: "Others see you as capable, practical, and visionary. You appear to be a master builder.",
                33: "Others see you as healing, teaching, and compassionate. You appear to be a spiritual guide."
            }
        }
        
        # Default meanings for other number types
        default_meanings = {
            1: "Leadership, independence, new beginnings",
            2: "Cooperation, balance, relationships", 
            3: "Creativity, communication, joy",
            4: "Stability, hard work, foundation",
            5: "Freedom, adventure, change",
            6: "Nurturing, responsibility, home",
            7: "Spirituality, analysis, introspection",
            8: "Material success, power, achievement",
            9: "Humanitarian service, completion, wisdom",
            11: "Intuition, inspiration, enlightenment",
            22: "Master builder, practical visionary",
            33: "Master teacher, healer, guide"
        }
        
        number_meanings = meanings.get(number_type, {})
        return number_meanings.get(number, default_meanings.get(number, "Unknown meaning"))
    
    def create_full_reading(self, full_name: str, birth_date: datetime) -> Dict[str, Any]:
        """Create a complete numerology reading"""
        try:
            numbers = self.calculate_all_numbers(full_name, birth_date)
            
            reading = {
                "name": full_name,
                "birth_date": birth_date.strftime("%Y-%m-%d"),
                "numbers": numbers,
                "interpretations": {}
            }
            
            # Add interpretations for each number
            for number_type, value in numbers.items():
                reading["interpretations"][number_type] = {
                    "number": value,
                    "meaning": self.get_number_meaning(value, number_type)
                }
            
            return reading
            
        except Exception as e:
            logger.error(f"Full reading creation error: {e}")
            return {}
    
    def format_reading_for_display(self, reading: Dict[str, Any]) -> str:
        """Format numerology reading for text display"""
        try:
            lines = []
            lines.append(f"🔢 Numerology Reading for {reading['name']}")
            lines.append(f"📅 Birth Date: {reading['birth_date']}")
            lines.append("")
            
            number_names = {
                "life_path": "Life Path Number",
                "expression": "Expression Number", 
                "soul_urge": "Soul Urge Number",
                "personality": "Personality Number",
                "birth_day": "Birth Day Number",
                "attitude": "Attitude Number"
            }
            
            for number_type, interpretation in reading.get("interpretations", {}).items():
                name = number_names.get(number_type, number_type.title())
                number = interpretation["number"]
                meaning = interpretation["meaning"]
                
                lines.append(f"✨ {name}: {number}")
                lines.append(f"   {meaning}")
                lines.append("")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Reading formatting error: {e}")
            return "Error formatting numerology reading"


# Global numerology service instance
numerology_service = NumerologyService()
