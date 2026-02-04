"""
Spam Protection Middleware
Silently blocks users who send >5 messages in 5 seconds for 5 minutes
"""

import time
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class SpamProtectionMiddleware(BaseMiddleware):
    """
    Spam protection with silent 5-minute block
    - Tracks messages per user in 5-second windows
    - If >5 messages in 5 seconds: block for 5 minutes
    - Blocked users get NO response (silent drop)
    """
    
    def __init__(self):
        super().__init__()
        self.user_messages: Dict[int, list] = {}
        self.blocked: Dict[int, float] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Check for spam and silently drop if user is blocked
        """
        # Get user ID
        user = None
        if hasattr(event, 'from_user'):
            user = event.from_user
        elif hasattr(event, 'message') and hasattr(event.message, 'from_user'):
            user = event.message.from_user
        
        if not user:
            return await handler(event, data)
        
        user_id = user.id
        now = time.time()
        
        # Check if user is blocked
        if user_id in self.blocked:
            if self.blocked[user_id] > now:
                # Still blocked - silently drop
                logger.warning(f"🚫 Spam blocked: user {user_id}")
                return  # No response
            else:
                # Block expired - remove
                del self.blocked[user_id]
                logger.info(f"✅ Unblocked: user {user_id}")
        
        # Count messages in last 5 seconds
        timestamps = self.user_messages.get(user_id, [])
        timestamps = [t for t in timestamps if now - t < 5]
        timestamps.append(now)
        self.user_messages[user_id] = timestamps
        
        # Check for spam (>5 messages in 5 seconds)
        if len(timestamps) > 5:
            # Block user for 5 minutes
            self.blocked[user_id] = now + 300
            logger.warning(f"⚠️ Spam detected: user {user_id} blocked for 5 minutes")
            return  # Silently drop
        
        # Not spam - process normally
        return await handler(event, data)
