"""
User helper functions for creation, updates, and statistics
"""

from datetime import datetime
from typing import Optional, Dict, Any
import logging

system_logger = logging.getLogger(__name__)


async def create_or_update_user(
    db,
    telegram_id: int,
    username: Optional[str] = None,
    first_name: str = "Unknown",
    last_name: Optional[str] = None,
    language_code: Optional[str] = "en"
) -> bool:
    """
    Create new user or update existing user's basic info
    
    Args:
        db: MongoDB database instance
        telegram_id: Telegram user ID
        username: Telegram username
        first_name: User's first name
        last_name: User's last name
        language_code: User's language code
    
    Returns:
        bool: True if successful
    """
    try:
        now = datetime.utcnow()
        
        # Check if user exists
        existing_user = await db.users.find_one({"telegram_id": telegram_id})
        
        if existing_user:
            # Update existing user
            await db.users.update_one(
                {"telegram_id": telegram_id},
                {
                    "$set": {
                        "username": username,
                        "first_name": first_name,
                        "last_name": last_name,
                        "language_code": language_code,
                        "last_active": now,
                        "updated_at": now
                    }
                }
            )
        else:
            # Create new user
            user_data = {
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "language_code": language_code,
                "tier": "free",
                "total_requests": 0,
                "daily_requests": 0,
                "last_request_date": None,
                "join_date": now,
                "last_active": now,
                "total_searches": 0,
                "total_commands": 0,
                "modules_used": [],
                "created_at": now,
                "updated_at": None,
                "notifications_enabled": True
            }
            
            await db.users.insert_one(user_data)
        
        return True
        
    except Exception as e:
        system_logger.error(f"Failed to create/update user {telegram_id}: {str(e)}")
        return False


async def increment_user_stats(
    db,
    user_id: int,
    stat_name: str,
    increment: int = 1
) -> bool:
    """
    Increment a specific user statistic
    
    Args:
        db: MongoDB database instance
        user_id: Telegram user ID
        stat_name: Name of stat to increment (total_searches, total_commands, etc.)
        increment: Amount to increment by
    
    Returns:
        bool: True if successful
    """
    try:
        await db.users.update_one(
            {"telegram_id": user_id},
            {
                "$inc": {stat_name: increment},
                "$set": {"last_active": datetime.utcnow()}
            }
        )
        return True
        
    except Exception as e:
        system_logger.error(f"Failed to increment {stat_name} for user {user_id}: {str(e)}")
        return False


async def add_module_to_user(
    db,
    user_id: int,
    module_name: str
) -> bool:
    """
    Add module to user's modules_used list if not already present
    
    Args:
        db: MongoDB database instance
        user_id: Telegram user ID
        module_name: Module identifier (m1_ai, m2_breach, etc.)
    
    Returns:
        bool: True if successful
    """
    try:
        await db.users.update_one(
            {"telegram_id": user_id},
            {
                "$addToSet": {"modules_used": module_name},
                "$set": {"last_active": datetime.utcnow()}
            }
        )
        return True
        
    except Exception as e:
        system_logger.error(f"Failed to add module {module_name} for user {user_id}: {str(e)}")
        return False


async def get_user_stats(
    db,
    user_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get user statistics
    
    Args:
        db: MongoDB database instance
        user_id: Telegram user ID
    
    Returns:
        dict: User statistics or None
    """
    try:
        user = await db.users.find_one(
            {"telegram_id": user_id},
            {
                "total_searches": 1,
                "total_commands": 1,
                "modules_used": 1,
                "join_date": 1,
                "last_active": 1,
                "tier": 1
            }
        )
        return user
        
    except Exception as e:
        system_logger.error(f"Failed to get stats for user {user_id}: {str(e)}")
        return None
