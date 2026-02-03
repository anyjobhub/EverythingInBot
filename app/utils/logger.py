"""
Async logging utility for user activity tracking
Non-blocking, silent failure, comprehensive event logging
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4
import logging

# Setup Python logger for system errors only
system_logger = logging.getLogger(__name__)


async def log_event(
    db,
    user_id: int,
    event_type: str,
    query_text: Optional[str] = None,
    module: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> bool:
    """
    Log user event to search_logs collection
    
    Args:
        db: MongoDB database instance
        user_id: Telegram user ID
        event_type: Type of event (command, button, search, action)
        query_text: User input or action description
        module: Module name (m1_ai, m2_breach, etc.)
        metadata: Additional context dictionary
        ip_address: Client IP address
        user_agent: User agent string
    
    Returns:
        bool: True if logged successfully, False otherwise
    """
    try:
        # Prepare log entry
        log_entry = {
            "telegram_id": user_id,
            "event_type": event_type,
            "query_text": query_text,
            "module_name": module,
            "timestamp": datetime.utcnow(),
            "session_id": str(uuid4()),
            "metadata": metadata or {},
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        # Insert into search_logs collection
        await db.search_logs.insert_one(log_entry)
        
        # Update user statistics
        await update_user_stats(db, user_id, event_type, module)
        
        return True
        
    except Exception as e:
        # Silent failure - log to system only, don't break user flow
        system_logger.error(f"Failed to log event for user {user_id}: {str(e)}")
        return False


async def update_user_stats(
    db,
    user_id: int,
    event_type: str,
    module: Optional[str] = None
) -> bool:
    """
    Update user statistics counters
    
    Args:
        db: MongoDB database instance
        user_id: Telegram user ID
        event_type: Type of event
        module: Module name
    
    Returns:
        bool: True if updated successfully
    """
    try:
        update_data = {
            "$set": {
                "last_active": datetime.utcnow()
            },
            "$inc": {}
        }
        
        # Increment appropriate counters
        if event_type == "command":
            update_data["$inc"]["total_commands"] = 1
        elif event_type in ["search", "action"]:
            update_data["$inc"]["total_searches"] = 1
        
        # Add module to modules_used if not already present
        if module:
            update_data["$addToSet"] = {"modules_used": module}
        
        # Update user document
        await db.users.update_one(
            {"telegram_id": user_id},
            update_data
        )
        
        return True
        
    except Exception as e:
        system_logger.error(f"Failed to update user stats for {user_id}: {str(e)}")
        return False


async def log_command(
    db,
    user_id: int,
    command: str,
    module: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> bool:
    """
    Convenience function to log a command event
    """
    return await log_event(
        db=db,
        user_id=user_id,
        event_type="command",
        query_text=command,
        module=module,
        metadata=metadata,
        ip_address=ip_address,
        user_agent=user_agent
    )


async def log_button_click(
    db,
    user_id: int,
    button_data: str,
    module: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> bool:
    """
    Convenience function to log a button click event
    """
    return await log_event(
        db=db,
        user_id=user_id,
        event_type="button",
        query_text=button_data,
        module=module,
        metadata=metadata,
        ip_address=ip_address,
        user_agent=user_agent
    )


async def log_search(
    db,
    user_id: int,
    search_query: str,
    module: str,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> bool:
    """
    Convenience function to log a search event
    """
    return await log_event(
        db=db,
        user_id=user_id,
        event_type="search",
        query_text=search_query,
        module=module,
        metadata=metadata,
        ip_address=ip_address,
        user_agent=user_agent
    )


async def log_action(
    db,
    user_id: int,
    action: str,
    module: str,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> bool:
    """
    Convenience function to log a general action event
    """
    return await log_event(
        db=db,
        user_id=user_id,
        event_type="action",
        query_text=action,
        module=module,
        metadata=metadata,
        ip_address=ip_address,
        user_agent=user_agent
    )
