"""
Spam Protection Middleware
Detect and prevent spam, flooding, and abusive behavior
"""

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable, Set
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class SpamProtectionMiddleware(BaseMiddleware):
    """
    Middleware to detect and prevent spam
    Includes flood detection, duplicate message detection, and blacklisting
    """
    
    def __init__(
        self,
        flood_threshold: int = 5,
        flood_window: int = 5,
        duplicate_threshold: int = 3,
        ban_duration: int = 3600
    ):
        """
        Initialize spam protection
        
        Args:
            flood_threshold: Max messages in flood window
            flood_window: Time window for flood detection (seconds)
            duplicate_threshold: Max duplicate messages allowed
            ban_duration: Ban duration in seconds (default: 1 hour)
        """
        super().__init__()
        
        self.flood_threshold = flood_threshold
        self.flood_window = flood_window
        self.duplicate_threshold = duplicate_threshold
        self.ban_duration = ban_duration
        
        # Track user messages
        self.user_messages: Dict[int, list] = defaultdict(list)
        
        # Track message content for duplicate detection
        self.user_message_content: Dict[int, list] = defaultdict(list)
        
        # Blacklist (banned users)
        self.blacklist: Dict[int, datetime] = {}
        
        # Whitelist (admins, trusted users)
        self.whitelist: Set[int] = set()
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Check for spam before processing"""
        
        user_id = event.from_user.id
        now = datetime.utcnow()
        
        # Skip whitelist
        if user_id in self.whitelist:
            return await handler(event, data)
        
        # Check blacklist
        if user_id in self.blacklist:
            ban_until = self.blacklist[user_id]
            
            if now < ban_until:
                # Still banned
                remaining = int((ban_until - now).total_seconds())
                
                if isinstance(event, Message):
                    await event.answer(
                        f"🚫 <b>You are temporarily banned</b>\n\n"
                        f"Reason: Spam/Abuse detected\n"
                        f"Time remaining: <b>{remaining // 60} minutes</b>\n\n"
                        f"<i>Please respect the bot's usage policies.</i>"
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        f"🚫 Banned for {remaining // 60}m",
                        show_alert=True
                    )
                
                return
            else:
                # Ban expired
                del self.blacklist[user_id]
                logger.info(f"Ban expired for user {user_id}")
        
        # Only check messages (not callbacks)
        if isinstance(event, Message):
            # Flood detection
            if await self._check_flood(user_id, now, event):
                return
            
            # Duplicate message detection
            if event.text and await self._check_duplicate(user_id, event.text, now, event):
                return
        
        # Continue processing
        return await handler(event, data)
    
    async def _check_flood(self, user_id: int, now: datetime, event: Message) -> bool:
        """
        Check for message flooding
        
        Returns:
            True if flood detected (block message)
        """
        # Clean old messages
        cutoff = now - timedelta(seconds=self.flood_window)
        self.user_messages[user_id] = [
            timestamp for timestamp in self.user_messages[user_id]
            if timestamp > cutoff
        ]
        
        # Check flood
        message_count = len(self.user_messages[user_id])
        
        if message_count >= self.flood_threshold:
            # Flood detected - ban user
            ban_until = now + timedelta(seconds=self.ban_duration)
            self.blacklist[user_id] = ban_until
            
            logger.warning(
                f"Flood detected from user {user_id}: "
                f"{message_count} messages in {self.flood_window}s. Banned for {self.ban_duration}s"
            )
            
            await event.answer(
                f"🚫 <b>Spam Detected</b>\n\n"
                f"You have been temporarily banned for flooding.\n"
                f"Duration: <b>{self.ban_duration // 60} minutes</b>\n\n"
                f"<i>Detected: {message_count} messages in {self.flood_window} seconds</i>"
            )
            
            return True
        
        # Record message
        self.user_messages[user_id].append(now)
        return False
    
    async def _check_duplicate(
        self,
        user_id: int,
        text: str,
        now: datetime,
        event: Message
    ) -> bool:
        """
        Check for duplicate messages
        
        Returns:
            True if spam detected (block message)
        """
        # Clean old content (last 60 seconds)
        cutoff = now - timedelta(seconds=60)
        self.user_message_content[user_id] = [
            (content, timestamp) for content, timestamp in self.user_message_content[user_id]
            if timestamp > cutoff
        ]
        
        # Count duplicates
        duplicate_count = sum(
            1 for content, _ in self.user_message_content[user_id]
            if content == text
        )
        
        if duplicate_count >= self.duplicate_threshold:
            logger.warning(
                f"Duplicate spam from user {user_id}: "
                f"'{text[:50]}...' repeated {duplicate_count} times"
            )
            
            await event.answer(
                "⚠️ <b>Duplicate Message Detected</b>\n\n"
                "Please don't send the same message repeatedly."
            )
            
            return True
        
        # Record content
        self.user_message_content[user_id].append((text, now))
        return False
    
    def ban_user(self, user_id: int, duration: int = None):
        """
        Manually ban a user
        
        Args:
            user_id: User ID to ban
            duration: Ban duration in seconds (default: self.ban_duration)
        """
        duration = duration or self.ban_duration
        ban_until = datetime.utcnow() + timedelta(seconds=duration)
        self.blacklist[user_id] = ban_until
        
        logger.info(f"User {user_id} banned for {duration}s")
    
    def unban_user(self, user_id: int):
        """
        Unban a user
        
        Args:
            user_id: User ID to unban
        """
        if user_id in self.blacklist:
            del self.blacklist[user_id]
            logger.info(f"User {user_id} unbanned")
    
    def add_to_whitelist(self, user_id: int):
        """
        Add user to whitelist (bypass spam protection)
        
        Args:
            user_id: User ID to whitelist
        """
        self.whitelist.add(user_id)
        logger.info(f"User {user_id} added to whitelist")
    
    def remove_from_whitelist(self, user_id: int):
        """
        Remove user from whitelist
        
        Args:
            user_id: User ID to remove
        """
        self.whitelist.discard(user_id)
        logger.info(f"User {user_id} removed from whitelist")
    
    def get_blacklist(self) -> Dict[int, datetime]:
        """Get current blacklist"""
        return self.blacklist.copy()
    
    def get_whitelist(self) -> Set[int]:
        """Get current whitelist"""
        return self.whitelist.copy()
