import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    PreCheckoutQueryHandler, filters, ContextTypes
)

from src.config import settings, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
from src.models import User, Horoscope, TarotReading, Payment
from src.services.ai_service import ai_service
from src.services.astrology_service import astrology_service
from src.services.tarot_service import tarot_service
from src.services.numerology_service import numerology_service
from src.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)


class AstrologerBot:
    def __init__(self):
        self.application = None
        self.user_states = {}  # Store user conversation states
        
    async def initialize(self):
        """Initialize the bot application"""
        self.application = Application.builder().token(settings.telegram_bot_token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("horoscope", self.horoscope_command))
        self.application.add_handler(CommandHandler("tarot", self.tarot_command))
        self.application.add_handler(CommandHandler("natal", self.natal_command))
        self.application.add_handler(CommandHandler("numerology", self.numerology_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("profile", self.profile_command))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.LOCATION, self.handle_location))
        
        # Payment handlers
        self.application.add_handler(PreCheckoutQueryHandler(self.precheckout_callback))
        
        logger.info("Bot initialized successfully")
    
    async def get_or_create_user(self, telegram_user, db: AsyncSession) -> User:
        """Get existing user or create new one"""
        try:
            # Try to get existing user
            result = await db.execute(
                select(User).where(User.telegram_id == telegram_user.id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                # Create new user
                user = User(
                    telegram_id=telegram_user.id,
                    username=telegram_user.username,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name,
                    language_code=telegram_user.language_code or DEFAULT_LANGUAGE
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
                logger.info(f"Created new user: {user.telegram_id}")
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting/creating user: {e}")
            await db.rollback()
            raise
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            async with get_async_db() as db:
                user = await self.get_or_create_user(update.effective_user, db)
                
                # Check if user needs to complete onboarding
                if not user.birth_date:
                    await self.start_onboarding(update, context, user)
                else:
                    await self.show_main_menu(update, context, user)
                    
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")
    
    async def start_onboarding(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User):
        """Start the onboarding process"""
        # Language selection
        keyboard = []
        for code, name in SUPPORTED_LANGUAGES.items():
            keyboard.append([InlineKeyboardButton(name, callback_data=f"lang_{code}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🌟 Welcome to AstrologerBot! 🌟

I'm your personal AI astrologer, ready to provide you with:
✨ Personalized horoscopes
🔮 Tarot readings  
🪐 Natal chart analysis
🔢 Numerology insights
💬 AI-powered astrological guidance

First, please select your preferred language:
        """
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User):
        """Show the main menu"""
        keyboard = [
            [InlineKeyboardButton("🌟 Daily Horoscope", callback_data="horoscope_daily")],
            [InlineKeyboardButton("🔮 Tarot Reading", callback_data="tarot_menu")],
            [InlineKeyboardButton("🪐 Natal Chart", callback_data="natal_chart")],
            [InlineKeyboardButton("🔢 Numerology", callback_data="numerology")],
            [InlineKeyboardButton("💬 Ask AI", callback_data="ai_chat")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("💎 Subscribe", callback_data="subscribe")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        greeting = self.get_text("main_menu_greeting", user.language_code).format(
            name=user.first_name or "there"
        )
        
        if update.message:
            await update.message.reply_text(greeting, reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(greeting, reply_markup=reply_markup)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        try:
            async with get_async_db() as db:
                user = await self.get_or_create_user(update.effective_user, db)
                
                data = query.data
                
                if data.startswith("lang_"):
                    await self.handle_language_selection(update, context, user, data, db)
                elif data == "horoscope_daily":
                    await self.handle_daily_horoscope(update, context, user, db)
                elif data == "tarot_menu":
                    await self.show_tarot_menu(update, context, user)
                elif data.startswith("tarot_"):
                    await self.handle_tarot_selection(update, context, user, data, db)
                elif data == "natal_chart":
                    await self.handle_natal_chart(update, context, user, db)
                elif data == "numerology":
                    await self.handle_numerology(update, context, user, db)
                elif data == "ai_chat":
                    await self.start_ai_chat(update, context, user)
                elif data == "settings":
                    await self.show_settings(update, context, user)
                elif data == "subscribe":
                    await self.show_subscription_options(update, context, user)
                elif data == "back_main":
                    await self.show_main_menu(update, context, user)
                else:
                    await query.edit_message_text("Unknown option selected.")
                    
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await query.edit_message_text("Sorry, something went wrong. Please try again.")
    
    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                      user: User, data: str, db: AsyncSession):
        """Handle language selection during onboarding"""
        lang_code = data.split("_")[1]
        user.language_code = lang_code
        await db.commit()
        
        # Continue with birth data collection
        text = self.get_text("birth_date_request", lang_code)
        await update.callback_query.edit_message_text(text)
        
        # Set user state for birth data collection
        self.user_states[user.telegram_id] = {"step": "birth_date"}
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        try:
            async with get_async_db() as db:
                user = await self.get_or_create_user(update.effective_user, db)
                
                # Check if user is in a specific state (onboarding, etc.)
                user_state = self.user_states.get(user.telegram_id, {})
                
                if user_state.get("step") == "birth_date":
                    await self.handle_birth_date_input(update, context, user, db)
                elif user_state.get("step") == "birth_time":
                    await self.handle_birth_time_input(update, context, user, db)
                elif user_state.get("step") == "birth_place":
                    await self.handle_birth_place_input(update, context, user, db)
                elif user_state.get("step") == "ai_chat":
                    await self.handle_ai_chat_message(update, context, user, db)
                elif user_state.get("step") == "tarot_question":
                    await self.handle_tarot_question(update, context, user, db)
                else:
                    # Default: treat as AI chat if user has premium
                    if user.can_use_feature("ai_chat"):
                        await self.handle_ai_chat_message(update, context, user, db)
                    else:
                        await self.show_main_menu(update, context, user)
                        
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")
    
    async def handle_birth_date_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                    user: User, db: AsyncSession):
        """Handle birth date input during onboarding"""
        try:
            # Parse date input (support various formats)
            date_text = update.message.text.strip()
            birth_date = self.parse_date(date_text)
            
            if not birth_date:
                text = self.get_text("invalid_date", user.language_code)
                await update.message.reply_text(text)
                return
            
            user.birth_date = birth_date
            await db.commit()
            
            # Ask for birth time
            text = self.get_text("birth_time_request", user.language_code)
            await update.message.reply_text(text)
            
            self.user_states[user.telegram_id] = {"step": "birth_time"}
            
        except Exception as e:
            logger.error(f"Error handling birth date: {e}")
            text = self.get_text("invalid_date", user.language_code)
            await update.message.reply_text(text)
    
    def parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from various formats"""
        formats = [
            "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y",
            "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
            "%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_text, fmt)
            except ValueError:
                continue
        
        return None
    
    def get_text(self, key: str, language: str) -> str:
        """Get localized text"""
        texts = {
            "en": {
                "main_menu_greeting": "Hello {name}! 🌟\n\nWhat would you like to explore today?",
                "birth_date_request": "Please enter your birth date (DD.MM.YYYY or DD/MM/YYYY):",
                "birth_time_request": "Please enter your birth time (HH:MM) or type 'skip' if unknown:",
                "birth_place_request": "Please enter your birth place (city, country) or share your location:",
                "invalid_date": "Invalid date format. Please use DD.MM.YYYY or DD/MM/YYYY format.",
                "invalid_time": "Invalid time format. Please use HH:MM format or type 'skip'.",
                "onboarding_complete": "Great! Your profile is now complete. Let's explore your astrological insights!",
                "feature_not_available": "This feature is available for premium subscribers only. Use /subscribe to upgrade!",
                "daily_limit_reached": "You've reached your daily limit for this feature. Upgrade to premium for unlimited access!",
                "generating_horoscope": "✨ Generating your personalized horoscope...",
                "generating_tarot": "🔮 Drawing your tarot cards...",
                "generating_natal": "🪐 Calculating your natal chart...",
                "generating_numerology": "🔢 Calculating your numerology reading...",
                "error_occurred": "Sorry, an error occurred. Please try again later."
            },
            "ru": {
                "main_menu_greeting": "Привет, {name}! 🌟\n\nЧто бы вы хотели изучить сегодня?",
                "birth_date_request": "Пожалуйста, введите дату рождения (ДД.ММ.ГГГГ или ДД/ММ/ГГГГ):",
                "birth_time_request": "Пожалуйста, введите время рождения (ЧЧ:ММ) или напишите 'пропустить', если неизвестно:",
                "birth_place_request": "Пожалуйста, введите место рождения (город, страна) или поделитесь местоположением:",
                "invalid_date": "Неверный формат даты. Используйте формат ДД.ММ.ГГГГ или ДД/ММ/ГГГГ.",
                "invalid_time": "Неверный формат времени. Используйте формат ЧЧ:ММ или напишите 'пропустить'.",
                "onboarding_complete": "Отлично! Ваш профиль теперь заполнен. Давайте изучим ваши астрологические прозрения!",
                "feature_not_available": "Эта функция доступна только для премиум-подписчиков. Используйте /subscribe для обновления!",
                "daily_limit_reached": "Вы достигли дневного лимита для этой функции. Обновитесь до премиум для неограниченного доступа!",
                "generating_horoscope": "✨ Генерирую ваш персональный гороскоп...",
                "generating_tarot": "🔮 Тяну ваши карты Таро...",
                "generating_natal": "🪐 Рассчитываю вашу натальную карту...",
                "generating_numerology": "🔢 Рассчитываю ваше нумерологическое чтение...",
                "error_occurred": "Извините, произошла ошибка. Попробуйте позже."
            },
            "es": {
                "main_menu_greeting": "¡Hola {name}! 🌟\n\n¿Qué te gustaría explorar hoy?",
                "birth_date_request": "Por favor, ingresa tu fecha de nacimiento (DD.MM.AAAA o DD/MM/AAAA):",
                "birth_time_request": "Por favor, ingresa tu hora de nacimiento (HH:MM) o escribe 'saltar' si no la sabes:",
                "birth_place_request": "Por favor, ingresa tu lugar de nacimiento (ciudad, país) o comparte tu ubicación:",
                "invalid_date": "Formato de fecha inválido. Usa el formato DD.MM.AAAA o DD/MM/AAAA.",
                "invalid_time": "Formato de hora inválido. Usa el formato HH:MM o escribe 'saltar'.",
                "onboarding_complete": "¡Genial! Tu perfil está ahora completo. ¡Exploremos tus percepciones astrológicas!",
                "feature_not_available": "Esta función está disponible solo para suscriptores premium. ¡Usa /subscribe para actualizar!",
                "daily_limit_reached": "Has alcanzado tu límite diario para esta función. ¡Actualiza a premium para acceso ilimitado!",
                "generating_horoscope": "✨ Generando tu horóscopo personalizado...",
                "generating_tarot": "🔮 Sacando tus cartas de tarot...",
                "generating_natal": "🪐 Calculando tu carta natal...",
                "generating_numerology": "🔢 Calculando tu lectura numerológica...",
                "error_occurred": "Lo siento, ocurrió un error. Inténtalo más tarde."
            }
        }
        
        return texts.get(language, texts["en"]).get(key, texts["en"].get(key, "Text not found"))
    
    async def handle_birth_time_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                    user: User, db: AsyncSession):
        """Handle birth time input during onboarding"""
        try:
            time_text = update.message.text.strip().lower()
            
            if time_text in ['skip', 'пропустить', 'saltar']:
                user.birth_time = "12:00"  # Default to noon
            else:
                # Parse time input
                birth_time = self.parse_time(time_text)
                if not birth_time:
                    text = self.get_text("invalid_time", user.language_code)
                    await update.message.reply_text(text)
                    return
                user.birth_time = birth_time
            
            await db.commit()
            
            # Ask for birth place
            text = self.get_text("birth_place_request", user.language_code)
            await update.message.reply_text(text)
            
            self.user_states[user.telegram_id] = {"step": "birth_place"}
            
        except Exception as e:
            logger.error(f"Error handling birth time: {e}")
            text = self.get_text("invalid_time", user.language_code)
            await update.message.reply_text(text)
    
    async def handle_birth_place_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                     user: User, db: AsyncSession):
        """Handle birth place input during onboarding"""
        try:
            place_text = update.message.text.strip()
            
            # Try to get coordinates for the place
            try:
                lat, lon = await astrology_service.get_coordinates(place_text)
                timezone = astrology_service.get_timezone(lat, lon)
                
                user.birth_place = place_text
                user.birth_latitude = lat
                user.birth_longitude = lon
                user.birth_timezone = timezone
                
                await db.commit()
                
                # Complete onboarding
                text = self.get_text("onboarding_complete", user.language_code)
                await update.message.reply_text(text)
                
                # Clear user state
                if user.telegram_id in self.user_states:
                    del self.user_states[user.telegram_id]
                
                # Show main menu
                await self.show_main_menu(update, context, user)
                
            except Exception as e:
                logger.error(f"Geocoding error: {e}")
                await update.message.reply_text(
                    "Could not find that location. Please try again with a different format (e.g., 'New York, USA')."
                )
                
        except Exception as e:
            logger.error(f"Error handling birth place: {e}")
            await update.message.reply_text("Error processing location. Please try again.")
    
    def parse_time(self, time_text: str) -> Optional[str]:
        """Parse time from various formats"""
        import re
        
        # Match HH:MM format
        match = re.match(r'^(\d{1,2}):(\d{2})$', time_text)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"
        
        return None
    
    async def handle_daily_horoscope(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   user: User, db: AsyncSession):
        """Handle daily horoscope request"""
        try:
            # Check if user can use this feature
            if not user.can_use_feature("daily_horoscope"):
                text = self.get_text("daily_limit_reached", user.language_code)
                await update.callback_query.edit_message_text(text)
                return
            
            # Show generating message
            text = self.get_text("generating_horoscope", user.language_code)
            await update.callback_query.edit_message_text(text)
            
            # Prepare user data for horoscope generation
            user_data = {
                "birth_date": user.birth_date.strftime("%Y-%m-%d") if user.birth_date else None,
                "birth_time": user.birth_time,
                "birth_place": user.birth_place,
                "birth_latitude": user.birth_latitude,
                "birth_longitude": user.birth_longitude
            }
            
            # Generate horoscope
            horoscope_content = await ai_service.generate_horoscope(
                user_data, "daily", user.language_code
            )
            
            # Save to database
            horoscope = Horoscope(
                user_id=user.id,
                horoscope_type="daily",
                content=horoscope_content,
                date_for=datetime.now().date(),
                ai_model_used=settings.ai_model
            )
            db.add(horoscope)
            
            # Update user usage
            user.daily_horoscopes_used += 1
            await db.commit()
            
            # Send horoscope
            keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="back_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                f"🌟 Your Daily Horoscope\n\n{horoscope_content}",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error generating horoscope: {e}")
            text = self.get_text("error_occurred", user.language_code)
            await update.callback_query.edit_message_text(text)
    
    async def show_tarot_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User):
        """Show tarot reading options"""
        keyboard = [
            [InlineKeyboardButton("🃏 Single Card", callback_data="tarot_single")],
            [InlineKeyboardButton("🔮 Three Cards", callback_data="tarot_three")],
            [InlineKeyboardButton("💕 Relationship", callback_data="tarot_relationship")],
            [InlineKeyboardButton("💼 Career", callback_data="tarot_career")],
            [InlineKeyboardButton("🌟 Celtic Cross", callback_data="tarot_celtic")],
            [InlineKeyboardButton("🏠 Back", callback_data="back_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "🔮 Choose your tarot reading type:"
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def handle_tarot_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   user: User, data: str, db: AsyncSession):
        """Handle tarot reading selection"""
        try:
            # Check if user can use this feature
            if not user.can_use_feature("tarot_reading"):
                text = self.get_text("daily_limit_reached", user.language_code)
                await update.callback_query.edit_message_text(text)
                return
            
            spread_type = data.replace("tarot_", "")
            
            # Map callback data to spread types
            spread_mapping = {
                "single": "single",
                "three": "three_card", 
                "relationship": "relationship",
                "career": "career",
                "celtic": "celtic_cross"
            }
            
            actual_spread = spread_mapping.get(spread_type, "single")
            
            # Ask for question (optional)
            text = "Do you have a specific question for the cards? (Type your question or 'no' to skip)"
            await update.callback_query.edit_message_text(text)
            
            # Set user state
            self.user_states[user.telegram_id] = {
                "step": "tarot_question",
                "spread_type": actual_spread
            }
            
        except Exception as e:
            logger.error(f"Error handling tarot selection: {e}")
            text = self.get_text("error_occurred", user.language_code)
            await update.callback_query.edit_message_text(text)
    
    async def handle_tarot_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  user: User, db: AsyncSession):
        """Handle tarot question input"""
        try:
            question_text = update.message.text.strip()
            user_state = self.user_states.get(user.telegram_id, {})
            spread_type = user_state.get("spread_type", "single")
            
            question = None if question_text.lower() in ['no', 'нет', 'skip'] else question_text
            
            # Show generating message
            text = self.get_text("generating_tarot", user.language_code)
            await update.message.reply_text(text)
            
            # Create tarot reading
            reading = tarot_service.create_reading(spread_type, question)
            
            # Generate AI interpretation
            interpretation = await ai_service.generate_tarot_interpretation(
                reading["cards"], spread_type, question, user.language_code
            )
            
            # Save to database
            tarot_reading = TarotReading(
                user_id=user.id,
                reading_type=spread_type,
                question=question,
                cards_drawn=reading["cards"],
                interpretation=interpretation,
                ai_model_used=settings.ai_model
            )
            db.add(tarot_reading)
            
            # Update user usage
            user.weekly_tarot_readings_used += 1
            await db.commit()
            
            # Format and send reading
            cards_text = tarot_service.format_reading_for_display(reading)
            full_text = f"{cards_text}\n\n🔮 Interpretation:\n{interpretation}"
            
            keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="back_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(full_text, reply_markup=reply_markup)
            
            # Clear user state
            if user.telegram_id in self.user_states:
                del self.user_states[user.telegram_id]
                
        except Exception as e:
            logger.error(f"Error handling tarot question: {e}")
            text = self.get_text("error_occurred", user.language_code)
            await update.message.reply_text(text)
    
    async def handle_natal_chart(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                               user: User, db: AsyncSession):
        """Handle natal chart request"""
        try:
            # Check if user can use this feature
            if not user.can_use_feature("natal_chart"):
                text = self.get_text("feature_not_available", user.language_code)
                await update.callback_query.edit_message_text(text)
                return
            
            # Check if user has complete birth data
            if not all([user.birth_date, user.birth_latitude, user.birth_longitude]):
                text = "Complete birth data (date, time, place) is required for natal chart calculation."
                await update.callback_query.edit_message_text(text)
                return
            
            # Show generating message
            text = self.get_text("generating_natal", user.language_code)
            await update.callback_query.edit_message_text(text)
            
            # Calculate natal chart
            birth_datetime = datetime.combine(
                user.birth_date.date(),
                datetime.strptime(user.birth_time, "%H:%M").time()
            )
            
            chart_data = astrology_service.calculate_natal_chart(
                birth_datetime, user.birth_latitude, user.birth_longitude
            )
            
            # Generate AI interpretation
            interpretation = await ai_service.generate_natal_chart_interpretation(
                chart_data, user.language_code
            )
            
            # Format response
            response_text = f"🪐 Your Natal Chart\n\n{interpretation}"
            
            keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="back_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(response_text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error handling natal chart: {e}")
            text = self.get_text("error_occurred", user.language_code)
            await update.callback_query.edit_message_text(text)
    
    async def handle_numerology(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                              user: User, db: AsyncSession):
        """Handle numerology request"""
        try:
            # Check if user can use this feature
            if not user.can_use_feature("numerology"):
                text = self.get_text("feature_not_available", user.language_code)
                await update.callback_query.edit_message_text(text)
                return
            
            # Check if user has required data
            if not user.birth_date:
                text = "Birth date is required for numerology calculation."
                await update.callback_query.edit_message_text(text)
                return
            
            # Show generating message
            text = self.get_text("generating_numerology", user.language_code)
            await update.callback_query.edit_message_text(text)
            
            # Calculate numerology
            full_name = user.full_name
            reading = numerology_service.create_full_reading(full_name, user.birth_date)
            
            # Generate AI interpretation
            interpretation = await ai_service.generate_numerology_reading(
                reading["numbers"], user.birth_date.strftime("%Y-%m-%d"), 
                full_name, user.language_code
            )
            
            # Format response
            basic_reading = numerology_service.format_reading_for_display(reading)
            response_text = f"{basic_reading}\n\n🔮 AI Interpretation:\n{interpretation}"
            
            keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="back_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(response_text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error handling numerology: {e}")
            text = self.get_text("error_occurred", user.language_code)
            await update.callback_query.edit_message_text(text)
    
    async def start_ai_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User):
        """Start AI chat mode"""
        if not user.can_use_feature("ai_chat"):
            text = self.get_text("feature_not_available", user.language_code)
            await update.callback_query.edit_message_text(text)
            return
        
        text = "💬 AI Chat Mode activated! Ask me anything about astrology, your life, or seek guidance. Type 'exit' to return to main menu."
        await update.callback_query.edit_message_text(text)
        
        # Set user state
        self.user_states[user.telegram_id] = {"step": "ai_chat"}
    
    async def handle_ai_chat_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   user: User, db: AsyncSession):
        """Handle AI chat messages"""
        try:
            message_text = update.message.text.strip()
            
            if message_text.lower() in ['exit', 'выход', 'salir']:
                # Clear user state and return to main menu
                if user.telegram_id in self.user_states:
                    del self.user_states[user.telegram_id]
                await self.show_main_menu(update, context, user)
                return
            
            # Prepare user context
            user_context = {
                "birth_date": user.birth_date.strftime("%Y-%m-%d") if user.birth_date else None,
                "birth_time": user.birth_time,
                "birth_place": user.birth_place
            }
            
            # Generate AI response
            response = await ai_service.chat_response(
                message_text, user_context, user.language_code
            )
            
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            text = self.get_text("error_occurred", user.language_code)
            await update.message.reply_text(text)
    
    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User):
        """Show user settings"""
        keyboard = [
            [InlineKeyboardButton("🌍 Change Language", callback_data="settings_language")],
            [InlineKeyboardButton("⏰ Horoscope Time", callback_data="settings_time")],
            [InlineKeyboardButton("👤 Edit Profile", callback_data="settings_profile")],
            [InlineKeyboardButton("🏠 Back", callback_data="back_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        status = "Premium ✨" if user.is_premium else "Free"
        text = f"""⚙️ Settings

👤 Profile: {user.full_name}
📅 Birth Date: {user.birth_date.strftime('%d.%m.%Y') if user.birth_date else 'Not set'}
🌍 Language: {SUPPORTED_LANGUAGES.get(user.language_code, 'Unknown')}
⏰ Daily Horoscope: {user.preferred_horoscope_time}
💎 Status: {status}

Choose what you'd like to change:"""
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def show_subscription_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User):
        """Show subscription options"""
        keyboard = [
            [InlineKeyboardButton("💎 Monthly - $9.90", callback_data="sub_monthly")],
            [InlineKeyboardButton("💎 Yearly - $99.00", callback_data="sub_yearly")],
            [InlineKeyboardButton("🏠 Back", callback_data="back_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """💎 Premium Subscription

Unlock all features:
✨ Unlimited daily horoscopes
🔮 Unlimited tarot readings
🪐 Detailed natal charts
🔢 Complete numerology reports
💬 AI astrologer chat
📊 Advanced insights

Choose your plan:"""
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    # Command handlers
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🌟 AstrologerBot Help

Available commands:
/start - Start the bot and setup profile
/horoscope - Get your daily horoscope
/tarot - Get a tarot reading
/natal - View your natal chart
/numerology - Get numerology insights
/subscribe - Upgrade to premium
/settings - Change your preferences
/profile - View your profile

Features:
✨ Personalized horoscopes
🔮 AI-powered tarot readings
🪐 Professional natal charts
🔢 Detailed numerology
💬 AI astrologer chat (Premium)

Need help? Just ask me anything!
        """
        await update.message.reply_text(help_text)
    
    async def horoscope_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /horoscope command"""
        try:
            async with get_async_db() as db:
                user = await self.get_or_create_user(update.effective_user, db)
                await self.handle_daily_horoscope(update, context, user, db)
        except Exception as e:
            logger.error(f"Error in horoscope command: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")
    
    async def tarot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /tarot command"""
        try:
            async with get_async_db() as db:
                user = await self.get_or_create_user(update.effective_user, db)
                await self.show_tarot_menu(update, context, user)
        except Exception as e:
            logger.error(f"Error in tarot command: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")
    
    async def natal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /natal command"""
        try:
            async with get_async_db() as db:
                user = await self.get_or_create_user(update.effective_user, db)
                await self.handle_natal_chart(update, context, user, db)
        except Exception as e:
            logger.error(f"Error in natal command: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")
    
    async def numerology_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /numerology command"""
        try:
            async with get_async_db() as db:
                user = await self.get_or_create_user(update.effective_user, db)
                await self.handle_numerology(update, context, user, db)
        except Exception as e:
            logger.error(f"Error in numerology command: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command"""
        try:
            async with get_async_db() as db:
                user = await self.get_or_create_user(update.effective_user, db)
                await self.show_subscription_options(update, context, user)
        except Exception as e:
            logger.error(f"Error in subscribe command: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        try:
            async with get_async_db() as db:
                user = await self.get_or_create_user(update.effective_user, db)
                await self.show_settings(update, context, user)
        except Exception as e:
            logger.error(f"Error in settings command: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command"""
        try:
            async with get_async_db() as db:
                user = await self.get_or_create_user(update.effective_user, db)
                
                status = "Premium ✨" if user.is_premium else "Free"
                profile_text = f"""👤 Your Profile

Name: {user.full_name}
Birth Date: {user.birth_date.strftime('%d.%m.%Y') if user.birth_date else 'Not set'}
Birth Time: {user.birth_time or 'Not set'}
Birth Place: {user.birth_place or 'Not set'}
Language: {SUPPORTED_LANGUAGES.get(user.language_code, 'Unknown')}
Status: {status}
Daily Horoscope Time: {user.preferred_horoscope_time}

Usage Today:
Daily Horoscopes: {user.daily_horoscopes_used}
Weekly Tarot Readings: {user.weekly_tarot_readings_used}"""
                
                await update.message.reply_text(profile_text)
        except Exception as e:
            logger.error(f"Error in profile command: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")
    
    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle location sharing"""
        try:
            async with get_async_db() as db:
                user = await self.get_or_create_user(update.effective_user, db)
                user_state = self.user_states.get(user.telegram_id, {})
                
                if user_state.get("step") == "birth_place":
                    location = update.message.location
                    
                    # Use shared location
                    user.birth_latitude = location.latitude
                    user.birth_longitude = location.longitude
                    user.birth_timezone = astrology_service.get_timezone(location.latitude, location.longitude)
                    user.birth_place = f"Lat: {location.latitude:.2f}, Lon: {location.longitude:.2f}"
                    
                    await db.commit()
                    
                    # Complete onboarding
                    text = self.get_text("onboarding_complete", user.language_code)
                    await update.message.reply_text(text)
                    
                    # Clear user state
                    if user.telegram_id in self.user_states:
                        del self.user_states[user.telegram_id]
                    
                    # Show main menu
                    await self.show_main_menu(update, context, user)
                    
        except Exception as e:
            logger.error(f"Error handling location: {e}")
            await update.message.reply_text("Error processing location. Please try again.")
    
    async def precheckout_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pre-checkout queries for payments"""
        query = update.pre_checkout_query
        await query.answer(ok=True)
    
    async def run_webhook(self, webhook_url: str):
        """Run bot with webhook"""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_webhook(
            listen="0.0.0.0",
            port=8000,
            webhook_url=webhook_url
        )
    
    async def run_polling(self):
        """Run bot with polling"""
        await self.application.initialize()
        await self.application.run_polling()


# Global bot instance
bot = AstrologerBot()
