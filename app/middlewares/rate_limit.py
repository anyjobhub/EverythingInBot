"""
Rate Limiting Middleware
Prevent abuse by limiting user actions per time window
"""

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware to rate limit user actions
    Prevents spam and abuse
    """
    
    def __init__(
        self,
        message_limit: int = 10,
        message_window: int = 60,
        command_limit: int = 5,
        command_window: int = 60,
        callback_limit: int = 20,
        callback_window: int = 60
    ):
        """
        Initialize rate limiter
        
        Args:
            message_limit: Max messages per window
            message_window: Time window in seconds for messages
            command_limit: Max commands per window
            command_window: Time window in seconds for commands
            callback_limit: Max callbacks per window
            callback_window: Time window in seconds for callbacks
        """
        super().__init__()
        
        # Limits configuration
        self.limits = {
            'message': (message_limit, message_window),
            'command': (command_limit, command_window),
            'callback': (callback_limit, callback_window)
        }
        
        # Track user actions
        self.user_actions: Dict[int, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        
        # Cooldown tracking
        self.user_cooldowns: Dict[int, datetime] = {}
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Check rate limit before processing"""
        
        user_id = event.from_user.id
        now = datetime.utcnow()
        
        # Check if user is in cooldown
        if user_id in self.user_cooldowns:
            cooldown_until = self.user_cooldowns[user_id]
            if now < cooldown_until:
                remaining = int((cooldown_until - now).total_seconds())
                
                if isinstance(event, Message):
                    await event.answer(
                        f"⏳ <b>Rate Limit</b>\n\n"
                        f"You're sending too many requests.\n"
                        f"Please wait <b>{remaining} seconds</b> before trying again."
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        f"⏳ Please wait {remaining}s",
                        show_alert=True
                    )
                return
            else:
                # Cooldown expired
                del self.user_cooldowns[user_id]
        
        # Determine action type
        if isinstance(event, Message):
            action_type = 'command' if event.text and event.text.startswith('/') else 'message'
        elif isinstance(event, CallbackQuery):
            action_type = 'callback'
        else:
            action_type = 'message'
        
        # Get limits for this action type
        limit, window = self.limits[action_type]
        
        # Clean old actions outside the time window
        cutoff_time = now - timedelta(seconds=window)
        self.user_actions[user_id][action_type] = [
            timestamp for timestamp in self.user_actions[user_id][action_type]
            if timestamp > cutoff_time
        ]
        
        # Check if limit exceeded
        action_count = len(self.user_actions[user_id][action_type])
        
        if action_count >= limit:
            # Apply cooldown (30 seconds)
            cooldown_duration = 30
            self.user_cooldowns[user_id] = now + timedelta(seconds=cooldown_duration)
            
            logger.warning(
                f"Rate limit exceeded for user {user_id}: "
                f"{action_count} {action_type}s in {window}s"
            )
            
            if isinstance(event, Message):
                await event.answer(
                    f"⚠️ <b>Rate Limit Exceeded</b>\n\n"
                    f"You've sent too many {action_type}s.\n"
                    f"Cooldown: <b>{cooldown_duration} seconds</b>\n\n"
                    f"<i>Limit: {limit} {action_type}s per {window} seconds</i>"
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    f"⚠️ Too many requests! Wait {cooldown_duration}s",
                    show_alert=True
                )
            
            return
        
        # Record this action
        self.user_actions[user_id][action_type].append(now)
        
        # Continue processing
        return await handler(event, data)
    
    def reset_user(self, user_id: int):
        """
        Reset rate limit for a user (admin override)
        
        Args:
            user_id: User ID to reset
        """
        if user_id in self.user_actions:
            del self.user_actions[user_id]
        if user_id in self.user_cooldowns:
            del self.user_cooldowns[user_id]
        
        logger.info(f"Rate limit reset for user {user_id}")
    
    def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """
        Get rate limit stats for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with action counts
        """
        return {
            action_type: len(timestamps)
            for action_type, timestamps in self.user_actions[user_id].items()
        }
