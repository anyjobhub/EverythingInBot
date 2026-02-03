"""
Input Validation Middleware
Sanitize and validate all user inputs to prevent injection attacks
"""

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import re
import html
import logging

logger = logging.getLogger(__name__)


class InputValidationMiddleware(BaseMiddleware):
    """
    Middleware to validate and sanitize user inputs
    Prevents XSS, injection attacks, and malformed data
    """
    
    def __init__(self, max_length: int = 1000):
        """
        Initialize validation middleware
        
        Args:
            max_length: Maximum allowed text length
        """
        super().__init__()
        self.max_length = max_length
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Process and validate input"""
        
        # Validate Message
        if isinstance(event, Message):
            if event.text:
                # Sanitize text
                original_text = event.text
                event.text = self.sanitize_text(event.text)
                
                # Log if text was modified
                if original_text != event.text:
                    logger.warning(
                        f"Sanitized input from user {event.from_user.id}: "
                        f"{original_text[:50]}... -> {event.text[:50]}..."
                    )
                
                # Validate length
                if len(event.text) > self.max_length:
                    await event.answer(
                        f"⚠️ Message too long. Maximum {self.max_length} characters allowed."
                    )
                    return
            
            # Validate caption
            if event.caption:
                event.caption = self.sanitize_text(event.caption)
        
        # Validate CallbackQuery data
        elif isinstance(event, CallbackQuery):
            if event.data:
                event.data = self.sanitize_callback_data(event.data)
        
        # Continue processing
        return await handler(event, data)
    
    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text input
        
        Args:
            text: Raw text input
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove HTML tags (prevent XSS)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Escape HTML entities
        text = html.escape(text)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Trim
        text = text.strip()
        
        return text
    
    def sanitize_callback_data(self, data: str) -> str:
        """
        Sanitize callback data
        
        Args:
            data: Callback data string
            
        Returns:
            Sanitized callback data
        """
        if not data:
            return ""
        
        # Allow only alphanumeric, underscore, hyphen, colon
        data = re.sub(r'[^a-zA-Z0-9_\-:]', '', data)
        
        # Limit length
        data = data[:64]
        
        return data
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address
            
        Returns:
            True if valid email format
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format
        
        Args:
            url: URL string
            
        Returns:
            True if valid URL format
        """
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\-.]', '_', filename)
        
        # Limit length
        filename = filename[:255]
        
        return filename
