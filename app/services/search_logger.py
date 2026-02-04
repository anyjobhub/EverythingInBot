"""
Search Logger Service
Handles logging of user searches to MongoDB
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from app.database import Database
from app.models.search_log import SearchLog

logger = logging.getLogger(__name__)


class SearchLogger:
    """
    Service for logging user searches
    Supports ephemeral mode with auto-delete
    """
    
    @staticmethod
    async def log_search(
        user_id: int,
        query: str,
        result_message_id: int,
        chat_id: int,
        module_name: str,
        username: Optional[str] = None,
        is_admin: bool = False,
        expiry_seconds: int = 300,
        **metadata
    ) -> str:
        """
        Log a search query to MongoDB
        
        Args:
            user_id: Telegram user ID
            query: Search query text
            result_message_id: Message ID of the result
            chat_id: Chat ID where result was sent
            module_name: Module name (m3_courses, m4_jobs, etc.)
            username: User's username
            is_admin: Whether user is admin
            expiry_seconds: Seconds until expiry (default: 300)
            **metadata: Additional metadata to store
        
        Returns:
            Inserted document ID as string
        """
        try:
            # Create search log
            search_log = SearchLog.create_ephemeral(
                telegram_id=user_id,
                query_text=query,
                result_message_id=result_message_id,
                chat_id=chat_id,
                module_name=module_name,
                username=username,
                is_admin=is_admin,
                expiry_seconds=expiry_seconds,
                **metadata
            )
            
            # Insert to MongoDB
            db = Database.get_db()
            result = await db.search_logs.insert_one(search_log.to_dict())
            
            logger.info(
                f"Logged search: user={user_id}, query='{query[:50]}', "
                f"module={module_name}, admin={is_admin}"
            )
            
            return str(result.inserted_id)
        
        except Exception as e:
            logger.error(f"Failed to log search: {e}")
            # Don't fail the request if logging fails
            return ""
    
    @staticmethod
    async def mark_as_deleted(
        result_message_id: int,
        chat_id: int
    ) -> bool:
        """
        Mark a search result as deleted
        
        Args:
            result_message_id: Message ID that was deleted
            chat_id: Chat ID
        
        Returns:
            True if updated successfully
        """
        try:
            db = Database.get_db()
            result = await db.search_logs.update_one(
                {
                    "result_message_id": result_message_id,
                    "chat_id": chat_id
                },
                {
                    "$set": {
                        "deleted": True,
                        "deleted_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Marked message {result_message_id} as deleted")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to mark as deleted: {e}")
            return False
    
    @staticmethod
    async def get_user_searches(
        user_id: int,
        limit: int = 50
    ) -> list[Dict[str, Any]]:
        """
        Get user's search history
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of results
        
        Returns:
            List of search logs
        """
        try:
            db = Database.get_db()
            cursor = db.search_logs.find(
                {"telegram_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            searches = await cursor.to_list(length=limit)
            return searches
        
        except Exception as e:
            logger.error(f"Failed to get user searches: {e}")
            return []
    
    @staticmethod
    async def get_all_searches(
        limit: int = 50,
        skip: int = 0
    ) -> list[Dict[str, Any]]:
        """
        Get all searches (admin only)
        
        Args:
            limit: Maximum number of results
            skip: Number of results to skip (pagination)
        
        Returns:
            List of search logs
        """
        try:
            db = Database.get_db()
            cursor = db.search_logs.find(
                {"event_type": "search"}
            ).sort("timestamp", -1).skip(skip).limit(limit)
            
            searches = await cursor.to_list(length=limit)
            return searches
        
        except Exception as e:
            logger.error(f"Failed to get all searches: {e}")
            return []
    
    @staticmethod
    async def get_search_stats() -> Dict[str, Any]:
        """
        Get search statistics
        
        Returns:
            Dictionary with stats
        """
        try:
            db = Database.get_db()
            
            total = await db.search_logs.count_documents({"event_type": "search"})
            deleted = await db.search_logs.count_documents({"deleted": True})
            active = total - deleted
            
            return {
                "total_searches": total,
                "deleted_messages": deleted,
                "active_messages": active
            }
        
        except Exception as e:
            logger.error(f"Failed to get search stats: {e}")
            return {}


# Singleton instance
search_logger = SearchLogger()
