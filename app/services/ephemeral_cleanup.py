"""
Ephemeral Cleanup Service
Handles automatic deletion of search result messages after expiry
"""

import asyncio
import logging
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from app.services.search_logger import search_logger

logger = logging.getLogger(__name__)


class EphemeralCleanup:
    """
    Service for managing ephemeral (auto-deleting) messages
    Messages are deleted after a specified delay
    """
    
    @staticmethod
    async def schedule_deletion(
        bot: Bot,
        chat_id: int,
        message_id: int,
        delay_seconds: int = 300,
        is_admin: bool = False
    ) -> None:
        """
        Schedule a message for deletion after delay
        
        IMPORTANT: This runs as a background task (non-blocking)
        Admin messages are never deleted
        
        Args:
            bot: Aiogram Bot instance
            chat_id: Chat ID where message was sent
            message_id: Message ID to delete
            delay_seconds: Delay before deletion (default: 300 = 5 minutes)
            is_admin: Whether user is admin (admins don't auto-delete)
        """
        # Admin messages don't auto-delete
        if is_admin:
            logger.info(f"Skipping auto-delete for admin message {message_id}")
            return
        
        try:
            logger.info(
                f"Scheduled deletion: chat={chat_id}, msg={message_id}, "
                f"delay={delay_seconds}s"
            )
            
            # Wait for the delay (non-blocking)
            await asyncio.sleep(delay_seconds)
            
            # Delete the message
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
            
            # Mark as deleted in database
            await search_logger.mark_as_deleted(message_id, chat_id)
            
            logger.info(f"Deleted ephemeral message: {message_id}")
        
        except TelegramBadRequest as e:
            # Message might already be deleted or not found
            logger.warning(f"Could not delete message {message_id}: {e}")
            # Still mark as deleted in DB
            await search_logger.mark_as_deleted(message_id, chat_id)
        
        except Exception as e:
            logger.error(f"Error deleting message {message_id}: {e}")
    
    @staticmethod
    def create_deletion_task(
        bot: Bot,
        chat_id: int,
        message_id: int,
        delay_seconds: int = 300,
        is_admin: bool = False
    ) -> asyncio.Task:
        """
        Create a background task for message deletion
        
        This is the recommended way to schedule deletions
        It doesn't block the webhook handler
        
        Args:
            bot: Aiogram Bot instance
            chat_id: Chat ID
            message_id: Message ID
            delay_seconds: Delay in seconds
            is_admin: Admin flag
        
        Returns:
            asyncio.Task that can be awaited or ignored
        
        Example:
            # In handler
            result_msg = await message.answer("Search results...")
            
            # Schedule deletion (non-blocking)
            EphemeralCleanup.create_deletion_task(
                bot=message.bot,
                chat_id=message.chat.id,
                message_id=result_msg.message_id,
                is_admin=is_admin
            )
        """
        task = asyncio.create_task(
            EphemeralCleanup.schedule_deletion(
                bot=bot,
                chat_id=chat_id,
                message_id=message_id,
                delay_seconds=delay_seconds,
                is_admin=is_admin
            )
        )
        
        return task
    
    @staticmethod
    async def delete_immediately(
        bot: Bot,
        chat_id: int,
        message_id: int
    ) -> bool:
        """
        Delete a message immediately (no delay)
        
        Args:
            bot: Aiogram Bot instance
            chat_id: Chat ID
            message_id: Message ID
        
        Returns:
            True if deleted successfully
        """
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
            await search_logger.mark_as_deleted(message_id, chat_id)
            logger.info(f"Immediately deleted message: {message_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete message {message_id}: {e}")
            return False
    
    @staticmethod
    async def handle_expired_interaction(
        message_id: int,
        chat_id: int
    ) -> str:
        """
        Generate message for expired search result interaction
        
        Args:
            message_id: Message ID that was interacted with
            chat_id: Chat ID
        
        Returns:
            Error message to show user
        """
        return (
            "⚠️ <b>This search result has expired</b>\n\n"
            "Search results are automatically deleted after 5 minutes.\n"
            "Please perform a new search to get fresh results."
        )


# Singleton instance
ephemeral_cleanup = EphemeralCleanup()
