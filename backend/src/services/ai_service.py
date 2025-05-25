import asyncio
import json
from typing import Dict, List, Optional, Any
import httpx
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.model = settings.ai_model
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://astrologer-bot.com",
                "X-Title": "Astrologer Telegram Bot"
            },
            timeout=60.0
        )
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate AI response using OpenRouter API"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            raise Exception(f"Failed to generate AI response: {str(e)}")
    
    async def generate_horoscope(
        self, 
        user_data: Dict[str, Any], 
        horoscope_type: str,
        language: str = "en"
    ) -> str:
        """Generate personalized horoscope"""
        
        # System prompt for horoscope generation
        system_prompt = self._get_horoscope_system_prompt(language)
        
        # User prompt with birth data
        user_prompt = self._build_horoscope_prompt(user_data, horoscope_type, language)
        
        return await self.generate_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=800,
            temperature=0.8
        )
    
    async def generate_tarot_interpretation(
        self,
        cards: List[Dict[str, Any]],
        reading_type: str,
        question: Optional[str] = None,
        language: str = "en"
    ) -> str:
        """Generate tarot reading interpretation"""
        
        system_prompt = self._get_tarot_system_prompt(language)
        user_prompt = self._build_tarot_prompt(cards, reading_type, question, language)
        
        return await self.generate_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=1200,
            temperature=0.9
        )
    
    async def generate_natal_chart_interpretation(
        self,
        chart_data: Dict[str, Any],
        language: str = "en"
    ) -> str:
        """Generate natal chart interpretation"""
        
        system_prompt = self._get_natal_chart_system_prompt(language)
        user_prompt = self._build_natal_chart_prompt(chart_data, language)
        
        return await self.generate_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=1500,
            temperature=0.7
        )
    
    async def generate_numerology_reading(
        self,
        numbers: Dict[str, int],
        birth_date: str,
        name: str,
        language: str = "en"
    ) -> str:
        """Generate numerology reading"""
        
        system_prompt = self._get_numerology_system_prompt(language)
        user_prompt = self._build_numerology_prompt(numbers, birth_date, name, language)
        
        return await self.generate_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=1000,
            temperature=0.8
        )
    
    async def chat_response(
        self,
        user_message: str,
        user_context: Dict[str, Any],
        language: str = "en"
    ) -> str:
        """Generate conversational response"""
        
        system_prompt = self._get_chat_system_prompt(language)
        user_prompt = self._build_chat_prompt(user_message, user_context, language)
        
        return await self.generate_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=600,
            temperature=0.8
        )
    
    def _get_horoscope_system_prompt(self, language: str) -> str:
        prompts = {
            "en": """You are a professional astrologer creating personalized horoscopes. 
                     Use the provided birth data to create accurate, insightful, and positive horoscopes.
                     Focus on practical advice and emotional guidance. Keep the tone warm and encouraging.
                     Avoid overly dramatic predictions. Length should be 3-4 paragraphs.""",
            "ru": """Вы профессиональный астролог, создающий персонализированные гороскопы.
                     Используйте предоставленные данные о рождении для создания точных, проницательных и позитивных гороскопов.
                     Сосредоточьтесь на практических советах и эмоциональном руководстве. Тон должен быть теплым и ободряющим.
                     Избегайте чрезмерно драматичных предсказаний. Длина должна быть 3-4 абзаца.""",
            "es": """Eres un astrólogo profesional creando horóscopos personalizados.
                     Usa los datos de nacimiento proporcionados para crear horóscopos precisos, perspicaces y positivos.
                     Enfócate en consejos prácticos y orientación emocional. Mantén un tono cálido y alentador.
                     Evita predicciones excesivamente dramáticas. La longitud debe ser de 3-4 párrafos."""
        }
        return prompts.get(language, prompts["en"])
    
    def _get_tarot_system_prompt(self, language: str) -> str:
        prompts = {
            "en": """You are an experienced tarot reader providing insightful interpretations.
                     Focus on the symbolic meanings of the cards and their positions in the spread.
                     Provide practical guidance and emotional insights. Be encouraging but honest.
                     Connect the cards to the user's question when provided.""",
            "ru": """Вы опытный таролог, предоставляющий проницательные интерпретации.
                     Сосредоточьтесь на символических значениях карт и их позициях в раскладе.
                     Предоставьте практическое руководство и эмоциональные озарения. Будьте ободряющими, но честными.
                     Свяжите карты с вопросом пользователя, если он предоставлен.""",
            "es": """Eres un lector de tarot experimentado proporcionando interpretaciones perspicaces.
                     Enfócate en los significados simbólicos de las cartas y sus posiciones en la tirada.
                     Proporciona orientación práctica y percepciones emocionales. Sé alentador pero honesto.
                     Conecta las cartas con la pregunta del usuario cuando se proporcione."""
        }
        return prompts.get(language, prompts["en"])
    
    def _get_natal_chart_system_prompt(self, language: str) -> str:
        prompts = {
            "en": """You are a professional astrologer interpreting natal charts.
                     Analyze the planetary positions, houses, and aspects to provide deep insights
                     into personality, life path, and potential. Be comprehensive but accessible.""",
            "ru": """Вы профессиональный астролог, интерпретирующий натальные карты.
                     Анализируйте позиции планет, дома и аспекты, чтобы предоставить глубокие озарения
                     о личности, жизненном пути и потенциале. Будьте всеобъемлющими, но доступными.""",
            "es": """Eres un astrólogo profesional interpretando cartas natales.
                     Analiza las posiciones planetarias, casas y aspectos para proporcionar percepciones profundas
                     sobre personalidad, camino de vida y potencial. Sé comprensivo pero accesible."""
        }
        return prompts.get(language, prompts["en"])
    
    def _get_numerology_system_prompt(self, language: str) -> str:
        prompts = {
            "en": """You are a numerology expert providing insights based on calculated numbers.
                     Explain the significance of each number and how they influence the person's life.
                     Focus on personality traits, life purpose, and guidance for personal growth.""",
            "ru": """Вы эксперт по нумерологии, предоставляющий озарения на основе вычисленных чисел.
                     Объясните значение каждого числа и то, как они влияют на жизнь человека.
                     Сосредоточьтесь на чертах личности, жизненной цели и руководстве для личностного роста.""",
            "es": """Eres un experto en numerología proporcionando percepciones basadas en números calculados.
                     Explica la importancia de cada número y cómo influyen en la vida de la persona.
                     Enfócate en rasgos de personalidad, propósito de vida y orientación para crecimiento personal."""
        }
        return prompts.get(language, prompts["en"])
    
    def _get_chat_system_prompt(self, language: str) -> str:
        prompts = {
            "en": """You are a wise and compassionate astrologer assistant.
                     Answer questions about astrology, spirituality, and life guidance.
                     Use the user's birth data when relevant. Be supportive and insightful.""",
            "ru": """Вы мудрый и сострадательный помощник астролога.
                     Отвечайте на вопросы об астрологии, духовности и жизненном руководстве.
                     Используйте данные о рождении пользователя, когда это уместно. Будьте поддерживающими и проницательными.""",
            "es": """Eres un asistente astrólogo sabio y compasivo.
                     Responde preguntas sobre astrología, espiritualidad y orientación de vida.
                     Usa los datos de nacimiento del usuario cuando sea relevante. Sé solidario y perspicaz."""
        }
        return prompts.get(language, prompts["en"])
    
    def _build_horoscope_prompt(self, user_data: Dict[str, Any], horoscope_type: str, language: str) -> str:
        """Build prompt for horoscope generation"""
        birth_info = f"""
Birth Date: {user_data.get('birth_date', 'Unknown')}
Birth Time: {user_data.get('birth_time', 'Unknown')}
Birth Place: {user_data.get('birth_place', 'Unknown')}
"""
        
        type_text = {
            "en": {"daily": "daily", "weekly": "weekly", "monthly": "monthly"},
            "ru": {"daily": "ежедневный", "weekly": "еженедельный", "monthly": "ежемесячный"},
            "es": {"daily": "diario", "weekly": "semanal", "monthly": "mensual"}
        }
        
        return f"""Create a {type_text[language][horoscope_type]} horoscope for a person with this birth data:
{birth_info}

Please provide a personalized {horoscope_type} horoscope that takes into account their astrological profile."""
    
    def _build_tarot_prompt(self, cards: List[Dict[str, Any]], reading_type: str, question: Optional[str], language: str) -> str:
        """Build prompt for tarot interpretation"""
        cards_text = "\n".join([f"{i+1}. {card['name']} - Position: {card.get('position', 'N/A')}" 
                               for i, card in enumerate(cards)])
        
        question_text = f"\nUser's Question: {question}" if question else ""
        
        return f"""Interpret this {reading_type} tarot reading:

Cards drawn:
{cards_text}{question_text}

Please provide a comprehensive interpretation of these cards and their meanings in relation to each other."""
    
    def _build_natal_chart_prompt(self, chart_data: Dict[str, Any], language: str) -> str:
        """Build prompt for natal chart interpretation"""
        return f"""Interpret this natal chart data:

{json.dumps(chart_data, indent=2)}

Please provide a comprehensive interpretation covering personality, life path, strengths, challenges, and guidance."""
    
    def _build_numerology_prompt(self, numbers: Dict[str, int], birth_date: str, name: str, language: str) -> str:
        """Build prompt for numerology reading"""
        numbers_text = "\n".join([f"{key}: {value}" for key, value in numbers.items()])
        
        return f"""Provide a numerology reading for:

Name: {name}
Birth Date: {birth_date}

Calculated Numbers:
{numbers_text}

Please interpret these numbers and their significance in this person's life."""
    
    def _build_chat_prompt(self, user_message: str, user_context: Dict[str, Any], language: str) -> str:
        """Build prompt for chat response"""
        context_info = ""
        if user_context.get('birth_date'):
            context_info = f"""
User's Birth Info:
- Date: {user_context.get('birth_date')}
- Time: {user_context.get('birth_time', 'Unknown')}
- Place: {user_context.get('birth_place', 'Unknown')}
"""
        
        return f"""User's question: {user_message}
{context_info}
Please provide a helpful and insightful response as an astrologer."""
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global AI service instance
ai_service = AIService()
