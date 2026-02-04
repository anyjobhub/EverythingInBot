"""
IP Tracking Middleware for Aiogram 3.x
Tracks user interactions for logging purposes
"""

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any, Awaitable
import logging

logger = logging.getLogger(__name__)


class IPTrackingMiddleware(BaseMiddleware):
    """
    Aiogram middleware to track user information
    Note: Telegram API doesn't provide IP addresses, so we track user_id instead
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Process update and extract user information
        """
        try:
            # Extract user information from event
            user = None
            chat = None
            
            if isinstance(event, Message):
                user = event.from_user
                chat = event.chat
            elif isinstance(event, CallbackQuery):
                user = event.from_user
                chat = event.message.chat if event.message else None
            
            # Store user information in data for handlers to access
            if user:
                data["user_id"] = user.id
                data["username"] = user.username or "unknown"
                data["first_name"] = user.first_name or "unknown"
                data["language_code"] = user.language_code or "unknown"
            
            if chat:
                data["chat_id"] = chat.id
                data["chat_type"] = chat.type
            
            # Note: IP address is not available from Telegram API
            # Telegram servers act as proxy, so we can't get real user IP
            data["ip_address"] = None
            
        except Exception as e:
            logger.error(f"Error in IP tracking middleware: {str(e)}")
            data["user_id"] = None
            data["username"] = "unknown"
        
        # Continue processing
        return await handler(event, data)
