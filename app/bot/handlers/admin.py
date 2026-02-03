"""
Admin Commands Handler
View user logs, search history, and platform statistics
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from datetime import datetime, timedelta
import json

from app.database import Database
from app.utils.logger import log_command

router = Router(name="admin")

# Admin user IDs (replace with actual admin IDs)
ADMIN_IDS = [123456789]  # Add your Telegram ID here


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS


@router.message(Command("user_logs"))
async def cmd_user_logs(message: Message):
    """View user activity logs"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Unauthorized. Admin only.")
        return
    
    db = Database.get_db()
    
    # Log admin command
    await log_command(db, message.from_user.id, "/user_logs", "admin")
    
    # Parse command arguments
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /user_logs <telegram_id>")
        return
    
    try:
        target_user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Invalid user ID")
        return
    
    # Get user logs
    logs = await db.search_logs.find(
        {"telegram_id": target_user_id}
    ).sort("timestamp", -1).limit(50).to_list(length=50)
    
    if not logs:
        await message.answer(f"No logs found for user {target_user_id}")
        return
    
    # Format logs
    log_text = f"📊 <b>User Logs for {target_user_id}</b>\n\n"
    log_text += f"Total logs: {len(logs)}\n\n"
    
    for i, log in enumerate(logs[:10], 1):
        timestamp = log.get("timestamp", datetime.utcnow())
        event_type = log.get("event_type", "unknown")
        query = log.get("query_text", "N/A")
        module = log.get("module_name", "N/A")
        
        log_text += f"{i}. [{timestamp.strftime('%Y-%m-%d %H:%M')}] "
        log_text += f"{event_type.upper()} - {module}\n"
        log_text += f"   Query: {query[:50]}...\n\n"
    
    await message.answer(log_text)


@router.message(Command("search_history"))
async def cmd_search_history(message: Message):
    """View user search history"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Unauthorized. Admin only.")
        return
    
    db = Database.get_db()
    
    # Log admin command
    await log_command(db, message.from_user.id, "/search_history", "admin")
    
    # Parse command arguments
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /search_history <telegram_id>")
        return
    
    try:
        target_user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Invalid user ID")
        return
    
    # Get search logs only
    searches = await db.search_logs.find(
        {
            "telegram_id": target_user_id,
            "event_type": {"$in": ["search", "action"]}
        }
    ).sort("timestamp", -1).limit(50).to_list(length=50)
    
    if not searches:
        await message.answer(f"No searches found for user {target_user_id}")
        return
    
    # Format searches
    search_text = f"🔍 <b>Search History for {target_user_id}</b>\n\n"
    search_text += f"Total searches: {len(searches)}\n\n"
    
    for i, search in enumerate(searches[:15], 1):
        timestamp = search.get("timestamp", datetime.utcnow())
        query = search.get("query_text", "N/A")
        module = search.get("module_name", "N/A")
        
        search_text += f"{i}. [{timestamp.strftime('%m-%d %H:%M')}] "
        search_text += f"<b>{module}</b>: {query[:40]}\n"
    
    await message.answer(search_text)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Platform statistics"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Unauthorized. Admin only.")
        return
    
    db = Database.get_db()
    
    # Log admin command
    await log_command(db, message.from_user.id, "/stats", "admin")
    
    await message.answer("📊 Generating statistics...")
    
    try:
        # Total users
        total_users = await db.users.count_documents({})
        
        # Active users (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_users = await db.users.count_documents({
            "last_active": {"$gte": seven_days_ago}
        })
        
        # Total searches
        total_searches = await db.search_logs.count_documents({})
        
        # Searches today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        searches_today = await db.search_logs.count_documents({
            "timestamp": {"$gte": today_start}
        })
        
        # Most used modules
        module_pipeline = [
            {"$match": {"module_name": {"$ne": None}}},
            {"$group": {"_id": "$module_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_modules = await db.search_logs.aggregate(module_pipeline).to_list(length=5)
        
        # Format stats
        stats_text = f"""
📊 <b>Platform Statistics</b>

<b>Users:</b>
• Total Users: {total_users}
• Active (7 days): {active_users}
• Active Rate: {(active_users/total_users*100) if total_users > 0 else 0:.1f}%

<b>Activity:</b>
• Total Searches: {total_searches}
• Searches Today: {searches_today}
• Avg per User: {(total_searches/total_users) if total_users > 0 else 0:.1f}

<b>Top Modules:</b>
"""
        
        for i, module in enumerate(top_modules, 1):
            module_name = module["_id"]
            count = module["count"]
            stats_text += f"{i}. {module_name}: {count} uses\n"
        
        stats_text += f"\n<b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
        
        await message.answer(stats_text)
        
    except Exception as e:
        await message.answer(f"❌ Error generating stats: {str(e)}")


@router.message(Command("export_user"))
async def cmd_export_user(message: Message):
    """Export all user data (admin)"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Unauthorized. Admin only.")
        return
    
    db = Database.get_db()
    
    # Parse command arguments
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /export_user <telegram_id>")
        return
    
    try:
        target_user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Invalid user ID")
        return
    
    await message.answer(f"📊 Exporting data for user {target_user_id}...")
    
    try:
        # Get user profile
        user = await db.users.find_one({"telegram_id": target_user_id})
        
        # Get all logs
        logs = await db.search_logs.find(
            {"telegram_id": target_user_id}
        ).sort("timestamp", -1).to_list(length=10000)
        
        if not user:
            await message.answer(f"❌ User {target_user_id} not found")
            return
        
        # Prepare export
        export_data = {
            "user_id": target_user_id,
            "export_date": datetime.utcnow().isoformat(),
            "user_profile": {
                "username": user.get("username"),
                "first_name": user.get("first_name"),
                "tier": user.get("tier"),
                "join_date": user.get("join_date").isoformat() if user.get("join_date") else None,
                "total_searches": user.get("total_searches", 0),
                "total_commands": user.get("total_commands", 0),
                "modules_used": user.get("modules_used", [])
            },
            "activity_logs": [
                {
                    "timestamp": log.get("timestamp").isoformat() if log.get("timestamp") else None,
                    "event_type": log.get("event_type"),
                    "query_text": log.get("query_text"),
                    "module_name": log.get("module_name"),
                    "metadata": log.get("metadata", {})
                }
                for log in logs
            ],
            "total_logs": len(logs)
        }
        
        # Convert to JSON
        json_export = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Send as file
        from io import BytesIO
        file_buffer = BytesIO(json_export.encode('utf-8'))
        file_buffer.name = f"user_{target_user_id}_export_{datetime.utcnow().strftime('%Y%m%d')}.json"
        
        await message.answer_document(
            document=file_buffer,
            caption=f"✅ <b>User Data Export</b>\n\nUser: {target_user_id}\nLogs: {len(logs)}"
        )
        
    except Exception as e:
        await message.answer(f"❌ Error exporting data: {str(e)}")
