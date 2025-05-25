import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.database import Base, async_engine
from src.handlers.bot import bot
from src.services.ai_service import ai_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Astrologer Bot application...")
    
    # Create database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")
    
    # Initialize bot
    await bot.initialize()
    logger.info("Bot initialized")
    
    # Start bot in background task
    if settings.telegram_webhook_url:
        # Use webhook mode
        asyncio.create_task(bot.run_webhook(settings.telegram_webhook_url))
        logger.info(f"Bot started in webhook mode: {settings.telegram_webhook_url}")
    else:
        # Use polling mode
        asyncio.create_task(bot.run_polling())
        logger.info("Bot started in polling mode")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await ai_service.close()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Astrologer Telegram Bot API",
    description="AI-powered astrological services via Telegram bot",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists(settings.static_files_path):
    app.mount("/static", StaticFiles(directory=settings.static_files_path), name="static")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Astrologer Bot API is running",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bot_status": "running" if bot.application else "not_initialized"
    }


@app.post("/webhook")
async def webhook_handler(request: dict):
    """Webhook endpoint for Telegram"""
    try:
        if bot.application:
            # Process the update
            from telegram import Update
            update = Update.de_json(request, bot.application.bot)
            await bot.application.process_update(update)
            return {"status": "ok"}
        else:
            return {"status": "error", "message": "Bot not initialized"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
