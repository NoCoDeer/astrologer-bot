import asyncio
import logging
from datetime import datetime, timedelta

from celery import Task
from sqlalchemy import select, delete, and_
from telegram import Bot

from src.celery_app import celery_app
from src.config import settings
from src.database import get_async_db
from src.models import User, Horoscope, TarotReading
from src.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class AsyncTask(Task):
    """Base task class for async operations"""
    
    def __call__(self, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.run_async(*args, **kwargs))
        finally:
            loop.close()
    
    async def run_async(self, *args, **kwargs):
        raise NotImplementedError


@celery_app.task(base=AsyncTask, bind=True)
async def send_daily_horoscopes(self):
    """Send daily horoscopes to users at their preferred time"""
    try:
        current_hour = datetime.now().hour
        
        async with get_async_db() as db:
            # Get users who should receive horoscope at this hour
            result = await db.execute(
                select(User).where(
                    and_(
                        User.preferred_horoscope_time.like(f"{current_hour:02d}:%"),
                        User.is_active == True,
                        User.birth_date.isnot(None)
                    )
                )
            )
            users = result.scalars().all()
            
            bot = Bot(token=settings.telegram_bot_token)
            sent_count = 0
            
            for user in users:
                try:
                    # Check if user already received horoscope today
                    today = datetime.now().date()
                    existing_horoscope = await db.execute(
                        select(Horoscope).where(
                            and_(
                                Horoscope.user_id == user.id,
                                Horoscope.date_for == today,
                                Horoscope.horoscope_type == "daily"
                            )
                        )
                    )
                    
                    if existing_horoscope.scalar_one_or_none():
                        continue  # Already sent today
                    
                    # Generate horoscope
                    user_data = {
                        "birth_date": user.birth_date.strftime("%Y-%m-%d") if user.birth_date else None,
                        "birth_time": user.birth_time,
                        "birth_place": user.birth_place,
                        "birth_latitude": user.birth_latitude,
                        "birth_longitude": user.birth_longitude
                    }
                    
                    horoscope_content = await ai_service.generate_horoscope(
                        user_data, "daily", user.language_code
                    )
                    
                    # Save to database
                    horoscope = Horoscope(
                        user_id=user.id,
                        horoscope_type="daily",
                        content=horoscope_content,
                        date_for=today,
                        ai_model_used=settings.ai_model
                    )
                    db.add(horoscope)
                    
                    # Send to user
                    message = f"🌟 Your Daily Horoscope for {today.strftime('%B %d, %Y')}\n\n{horoscope_content}"
                    await bot.send_message(chat_id=user.telegram_id, text=message)
                    
                    sent_count += 1
                    logger.info(f"Sent daily horoscope to user {user.telegram_id}")
                    
                except Exception as e:
                    logger.error(f"Error sending horoscope to user {user.telegram_id}: {e}")
                    continue
            
            await db.commit()
            logger.info(f"Sent {sent_count} daily horoscopes")
            
    except Exception as e:
        logger.error(f"Error in send_daily_horoscopes task: {e}")
        raise


@celery_app.task(base=AsyncTask, bind=True)
async def reset_usage_counters(self):
    """Reset daily/weekly usage counters"""
    try:
        async with get_async_db() as db:
            # Reset daily counters
            await db.execute(
                "UPDATE users SET daily_horoscopes_used = 0"
            )
            
            # Reset weekly counters on Mondays
            if datetime.now().weekday() == 0:  # Monday
                await db.execute(
                    "UPDATE users SET weekly_tarot_readings_used = 0"
                )
                logger.info("Reset weekly usage counters")
            
            await db.commit()
            logger.info("Reset daily usage counters")
            
    except Exception as e:
        logger.error(f"Error in reset_usage_counters task: {e}")
        raise


@celery_app.task(base=AsyncTask, bind=True)
async def cleanup_old_data(self):
    """Clean up old data to save storage space"""
    try:
        async with get_async_db() as db:
            # Delete horoscopes older than 30 days
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            
            result = await db.execute(
                delete(Horoscope).where(Horoscope.date_for < thirty_days_ago)
            )
            horoscopes_deleted = result.rowcount
            
            # Delete tarot readings older than 90 days
            ninety_days_ago = datetime.now() - timedelta(days=90)
            
            result = await db.execute(
                delete(TarotReading).where(TarotReading.created_at < ninety_days_ago)
            )
            tarot_deleted = result.rowcount
            
            await db.commit()
            logger.info(f"Cleaned up {horoscopes_deleted} old horoscopes and {tarot_deleted} old tarot readings")
            
    except Exception as e:
        logger.error(f"Error in cleanup_old_data task: {e}")
        raise


@celery_app.task(base=AsyncTask, bind=True)
async def send_mercury_retrograde_alert(self):
    """Send alerts about Mercury retrograde periods"""
    try:
        # This would require more complex astrological calculations
        # For now, this is a placeholder for future implementation
        logger.info("Mercury retrograde alert task executed (placeholder)")
        
    except Exception as e:
        logger.error(f"Error in mercury_retrograde_alert task: {e}")
        raise


@celery_app.task(base=AsyncTask, bind=True)
async def generate_weekly_insights(self):
    """Generate weekly astrological insights for premium users"""
    try:
        async with get_async_db() as db:
            # Get premium users
            result = await db.execute(
                select(User).where(
                    and_(
                        User.is_premium == True,
                        User.is_active == True,
                        User.birth_date.isnot(None)
                    )
                )
            )
            users = result.scalars().all()
            
            bot = Bot(token=settings.telegram_bot_token)
            sent_count = 0
            
            for user in users:
                try:
                    # Generate weekly horoscope
                    user_data = {
                        "birth_date": user.birth_date.strftime("%Y-%m-%d") if user.birth_date else None,
                        "birth_time": user.birth_time,
                        "birth_place": user.birth_place,
                        "birth_latitude": user.birth_latitude,
                        "birth_longitude": user.birth_longitude
                    }
                    
                    weekly_content = await ai_service.generate_horoscope(
                        user_data, "weekly", user.language_code
                    )
                    
                    # Save to database
                    horoscope = Horoscope(
                        user_id=user.id,
                        horoscope_type="weekly",
                        content=weekly_content,
                        date_for=datetime.now().date(),
                        ai_model_used=settings.ai_model
                    )
                    db.add(horoscope)
                    
                    # Send to user
                    message = f"🌟 Your Weekly Insights\n\n{weekly_content}"
                    await bot.send_message(chat_id=user.telegram_id, text=message)
                    
                    sent_count += 1
                    logger.info(f"Sent weekly insights to user {user.telegram_id}")
                    
                except Exception as e:
                    logger.error(f"Error sending weekly insights to user {user.telegram_id}: {e}")
                    continue
            
            await db.commit()
            logger.info(f"Sent {sent_count} weekly insights")
            
    except Exception as e:
        logger.error(f"Error in generate_weekly_insights task: {e}")
        raise


@celery_app.task(base=AsyncTask, bind=True)
async def backup_user_data(self):
    """Backup important user data"""
    try:
        # This would implement data backup logic
        # For now, this is a placeholder
        logger.info("User data backup task executed (placeholder)")
        
    except Exception as e:
        logger.error(f"Error in backup_user_data task: {e}")
        raise


# Additional scheduled tasks can be added here
# For example: moon phase notifications, planetary aspect alerts, etc.
