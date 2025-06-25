from typing import Optional
import logging
import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for Telegram Stars payments."""

    def __init__(self) -> None:
        self.token = settings.telegram_stars_token
        self.api_url = f"https://api.telegram.org/bot{self.token}" if self.token else None

    async def create_stars_invoice(self, title: str, description: str, payload: str, amount: int) -> Optional[str]:
        """Create invoice link using Telegram Stars API.

        Returns the invoice URL or None on failure.
        """
        if not self.api_url:
            logger.warning("Telegram Stars token not configured")
            return None

        url = f"{self.api_url}/createInvoiceLink"
        data = {
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": self.token,
            "currency": "USD",
            "prices": [{"label": title, "amount": amount}],
        }
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json=data)
                r.raise_for_status()
                resp = r.json()
                return resp.get("result")
        except Exception as e:
            logger.error(f"Failed to create invoice: {e}")
            return None


payment_service = PaymentService()
