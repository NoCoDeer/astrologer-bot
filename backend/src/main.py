import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy import select

from src.config import settings
from src.database import Base, async_engine, get_async_db
from src.models import User, Payment
from src.handlers.bot import bot
from src.services.ai_service import ai_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

security = HTTPBasic()


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Simple admin authentication."""
    if (
        credentials.username == settings.admin_username
        and credentials.password == settings.admin_password
    ):
        return credentials.username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Basic"},
    )


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


# -------------------- Admin Endpoints --------------------

@app.post("/admin/login")
async def admin_login(credentials: HTTPBasicCredentials = Depends(security)):
    if (
        credentials.username == settings.admin_username
        and credentials.password == settings.admin_password
    ):
        return {"status": "ok"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@app.get("/admin/users")
async def admin_users(admin: str = Depends(verify_admin)):
    async with get_async_db() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        return [
            {
                "id": u.id,
                "telegram_id": u.telegram_id,
                "username": u.username,
                "is_premium": u.is_premium,
                "created_at": u.created_at,
            }
            for u in users
        ]


@app.get("/admin/payments")
async def admin_payments(admin: str = Depends(verify_admin)):
    async with get_async_db() as db:
        result = await db.execute(select(Payment))
        payments = result.scalars().all()
        return [
            {
                "id": p.id,
                "user_id": p.user_id,
                "provider": p.provider,
                "amount": p.amount,
                "status": p.status,
                "paid_at": p.paid_at,
            }
            for p in payments
        ]


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
