"""
Admin Search Logs Handler
View all user search history (admin only)
"""

import logging
from datetime import datetime, timezone, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.config import settings
from app.services.search_logger import search_logger
from app.bot.keyboards.main_menu import get_back_to_menu_button

logger = logging.getLogger(__name__)
router = Router(name="admin_search")


# Admin user IDs (from config)
ADMIN_IDS = getattr(settings, 'ADMIN_IDS', [])


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS


def format_timestamp_ist(utc_timestamp: datetime) -> str:
    """
    Convert UTC timestamp to IST and format
    
    Args:
        utc_timestamp: UTC datetime
    
    Returns:
        Formatted IST timestamp
    """
    # IST is UTC+5:30
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = utc_timestamp + ist_offset
    return ist_time.strftime("%d %b %Y, %I:%M %p IST")


@router.message(Command("admin_search_logs"))
async def show_search_logs(message: Message, **data):
    """
    Show all user search logs (admin only)
    
    Usage: /admin_search_logs
    """
    # Check admin permission
    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔️ <b>Access Denied</b>\n\n"
            "This command is only available to administrators."
        )
        return
    
    try:
        # Get search statistics
        stats = await search_logger.get_search_stats()
        
        # Get last 50 searches
        searches = await search_logger.get_all_searches(limit=50)
        
        if not searches:
            await message.answer(
                "📊 <b>Search Logs</b>\n\n"
                "No search logs found.",
                reply_markup=get_back_to_menu_button()
            )
            return
        
        # Build response
        response = "📊 <b>Search Logs (Last 50)</b>\n\n"
        
        # Add statistics
        response += f"<b>Statistics:</b>\n"
        response += f"• Total Searches: {stats.get('total_searches', 0)}\n"
        response += f"• Active Messages: {stats.get('active_messages', 0)}\n"
        response += f"• Deleted Messages: {stats.get('deleted_messages', 0)}\n\n"
        
        response += "━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Add search entries
        for idx, search in enumerate(searches[:20], 1):  # Show first 20 in message
            user_id = search.get('telegram_id', 'Unknown')
            username = search.get('username', 'N/A')
            query = search.get('query_text', 'N/A')
            module = search.get('module_name', 'N/A')
            timestamp = search.get('timestamp')
            deleted = search.get('deleted', False)
            is_admin_user = search.get('is_admin', False)
            
            # Format timestamp
            time_str = format_timestamp_ist(timestamp) if timestamp else 'N/A'
            
            # Status emoji
            status_emoji = "🗑" if deleted else "✅"
            admin_badge = "👑" if is_admin_user else ""
            
            response += f"{idx}. {status_emoji} {admin_badge}\n"
            response += f"   <b>User:</b> {user_id} (@{username})\n"
            response += f"   <b>Query:</b> {query[:50]}...\n" if len(query) > 50 else f"   <b>Query:</b> {query}\n"
            response += f"   <b>Module:</b> {module}\n"
            response += f"   <b>Time:</b> {time_str}\n\n"
        
        # Add pagination info if more than 20
        if len(searches) > 20:
            response += f"\n<i>Showing 20 of {len(searches)} results</i>\n"
        
        # Create keyboard with refresh button
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="🔄 Refresh", callback_data="admin_refresh_logs")
        )
        builder.row(
            InlineKeyboardButton(text="📈 Stats", callback_data="admin_search_stats")
        )
        builder.row(
            InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
        )
        
        await message.answer(
            response,
            reply_markup=builder.as_markup()
        )
    
    except Exception as e:
        logger.error(f"Error showing search logs: {e}")
        await message.answer(
            "❌ <b>Error</b>\n\n"
            "Failed to retrieve search logs. Please try again later."
        )


@router.callback_query(F.data == "admin_refresh_logs")
async def refresh_logs(callback: CallbackQuery):
    """Refresh search logs"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Access Denied", show_alert=True)
        return
    
    try:
        # Get fresh data
        stats = await search_logger.get_search_stats()
        searches = await search_logger.get_all_searches(limit=50)
        
        # Build response (same as above)
        response = "📊 <b>Search Logs (Last 50)</b>\n\n"
        response += f"<b>Statistics:</b>\n"
        response += f"• Total Searches: {stats.get('total_searches', 0)}\n"
        response += f"• Active Messages: {stats.get('active_messages', 0)}\n"
        response += f"• Deleted Messages: {stats.get('deleted_messages', 0)}\n\n"
        response += "━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for idx, search in enumerate(searches[:20], 1):
            user_id = search.get('telegram_id', 'Unknown')
            username = search.get('username', 'N/A')
            query = search.get('query_text', 'N/A')
            module = search.get('module_name', 'N/A')
            timestamp = search.get('timestamp')
            deleted = search.get('deleted', False)
            is_admin_user = search.get('is_admin', False)
            
            time_str = format_timestamp_ist(timestamp) if timestamp else 'N/A'
            status_emoji = "🗑" if deleted else "✅"
            admin_badge = "👑" if is_admin_user else ""
            
            response += f"{idx}. {status_emoji} {admin_badge}\n"
            response += f"   <b>User:</b> {user_id} (@{username})\n"
            response += f"   <b>Query:</b> {query[:50]}...\n" if len(query) > 50 else f"   <b>Query:</b> {query}\n"
            response += f"   <b>Module:</b> {module}\n"
            response += f"   <b>Time:</b> {time_str}\n\n"
        
        if len(searches) > 20:
            response += f"\n<i>Showing 20 of {len(searches)} results</i>\n"
        
        # Update message
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="🔄 Refresh", callback_data="admin_refresh_logs")
        )
        builder.row(
            InlineKeyboardButton(text="📈 Stats", callback_data="admin_search_stats")
        )
        builder.row(
            InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
        )
        
        await callback.message.edit_text(
            response,
            reply_markup=builder.as_markup()
        )
        await callback.answer("✅ Refreshed")
    
    except Exception as e:
        logger.error(f"Error refreshing logs: {e}")
        await callback.answer("❌ Error refreshing", show_alert=True)


@router.callback_query(F.data == "admin_search_stats")
async def show_stats(callback: CallbackQuery):
    """Show detailed search statistics"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Access Denied", show_alert=True)
        return
    
    try:
        stats = await search_logger.get_search_stats()
        
        response = "📈 <b>Search Statistics</b>\n\n"
        response += f"<b>Total Searches:</b> {stats.get('total_searches', 0)}\n"
        response += f"<b>Active Messages:</b> {stats.get('active_messages', 0)}\n"
        response += f"<b>Deleted Messages:</b> {stats.get('deleted_messages', 0)}\n\n"
        
        if stats.get('total_searches', 0) > 0:
            deletion_rate = (stats.get('deleted_messages', 0) / stats.get('total_searches', 1)) * 100
            response += f"<b>Deletion Rate:</b> {deletion_rate:.1f}%\n"
        
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="🔙 Back to Logs", callback_data="admin_refresh_logs")
        )
        
        await callback.message.edit_text(
            response,
            reply_markup=builder.as_markup()
        )
        await callback.answer()
    
    except Exception as e:
        logger.error(f"Error showing stats: {e}")
        await callback.answer("❌ Error loading stats", show_alert=True)
