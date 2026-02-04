"""
Start Command Handler with Comprehensive Logging
Main menu, welcome message, profile, and privacy policy
"""

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json

from app.bot.keyboards.main_menu import get_main_menu_keyboard
from app.bot.keyboards.privacy import (
    get_privacy_keyboard, 
    get_back_from_privacy_keyboard, 
    PRIVACY_POLICY_TEXT, 
    SECURITY_DISCLAIMER
)
from app.database import Database
from app.utils.logger import log_command, log_button_click, log_action
from app.utils.user_helper import create_or_update_user, get_user_stats
from datetime import datetime

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Handle /start command with comprehensive logging
    Display main menu with all 10 modules
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("🔥 START HANDLER TRIGGERED!")
    logger.info(f"User: {message.from_user.id} (@{message.from_user.username})")
    logger.info(f"Message text: {message.text}")
    
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    first_name = message.from_user.first_name or "Unknown"
    last_name = message.from_user.last_name
    language_code = message.from_user.language_code or "en"
    
    # Get database
    db = Database.get_db()
    
    # Create or update user
    await create_or_update_user(
        db=db,
        telegram_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        language_code=language_code
    )
    
    # Log the start command
    await log_command(
        db=db,
        user_id=user_id,
        command="/start",
        module="start",
        metadata={
            "username": username,
            "first_name": first_name,
            "language_code": language_code
        }
    )
    
    # Welcome message with security disclaimer
    welcome_text = f"""
🌟 <b>Welcome to EverythingInBot!</b> 🌟

Hey <b>{first_name}</b>! 👋

I'm your all-in-one Telegram Super-App with <b>10 powerful modules</b>:

🤖 <b>AI Engine Hub</b> - GPT-4o, Claude, Gemini & more
🔐 <b>Breach Check</b> - Email & password security
📚 <b>Courses & Learning</b> - Hacking, coding, design
💼 <b>Jobs & Careers</b> - AI resume, interview prep
🛠 <b>Tools & Utilities</b> - PDF, image, text tools
✅ <b>Productivity</b> - To-do, notes, habits
👨‍💻 <b>Developer Tools</b> - JSON, regex, API tester
🔒 <b>Cybersecurity</b> - Nmap, logs, threat intel
🔍 <b>OSINT Tools</b> - WHOIS, DNS, IP lookup
🎮 <b>Entertainment</b> - Games, jokes, stories

{SECURITY_DISCLAIMER}

Choose a module below to get started! 👇
"""
    
    logger.info("✅ Sending welcome message...")
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard()
    )
    logger.info("✅ Welcome message sent successfully!")


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery):
    """Show main menu with logging"""
    user_id = callback.from_user.id
    db = Database.get_db()
    
    # Log button click
    await log_button_click(
        db=db,
        user_id=user_id,
        button_data="main_menu",
        module="start"
    )
    
    await callback.message.edit_text(
        "🏠 <b>Main Menu</b>\n\nSelect a module:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Help command with logging"""
    user_id = message.from_user.id
    db = Database.get_db()
    
    # Log command
    await log_command(
        db=db,
        user_id=user_id,
        command="/help",
        module="start"
    )
    
    help_text = """
📖 <b>EverythingInBot - Help</b>

<b>Commands:</b>
/start - Main menu
/help - This help message
/profile - Your profile & subscription
/privacy - Privacy & data policy
/export_history - Export your data
/upgrade - Upgrade to Pro

<b>Subscription Tiers:</b>
🆓 <b>Free</b> - 5 requests/day
⭐ <b>Pro</b> - Unlimited requests + premium features

<b>Need Support?</b>
Contact: @YourSupportBot
"""
    await message.answer(help_text)


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Show user profile with statistics"""
    user_id = message.from_user.id
    db = Database.get_db()
    
    # Log command
    await log_command(
        db=db,
        user_id=user_id,
        command="/profile",
        module="start"
    )
    
    # Get user stats
    user_stats = await get_user_stats(db, user_id)
    
    if not user_stats:
        await message.answer("❌ User not found. Please /start first.")
        return
    
    tier = user_stats.get("tier", "free").upper()
    total_searches = user_stats.get("total_searches", 0)
    total_commands = user_stats.get("total_commands", 0)
    modules_used = user_stats.get("modules_used", [])
    join_date = user_stats.get("join_date", datetime.utcnow())
    last_active = user_stats.get("last_active", datetime.utcnow())
    
    profile_text = f"""
👤 <b>Your Profile</b>

<b>Name:</b> {message.from_user.first_name}
<b>Username:</b> @{message.from_user.username or 'N/A'}
<b>Tier:</b> {tier}

<b>Activity Statistics:</b>
📊 Total Searches: {total_searches}
⌨️ Total Commands: {total_commands}
🎯 Modules Used: {len(modules_used)}/10

<b>Account Info:</b>
📅 Member Since: {join_date.strftime('%Y-%m-%d')}
🕐 Last Active: {last_active.strftime('%Y-%m-%d %H:%M')}

{f'⭐ You have unlimited access!' if tier == 'PRO' else '🆓 Upgrade to Pro for unlimited access!'}
"""
    
    await message.answer(profile_text)


@router.message(Command("privacy"))
async def cmd_privacy(message: Message):
    """Show privacy policy"""
    user_id = message.from_user.id
    db = Database.get_db()
    
    # Log command
    await log_command(
        db=db,
        user_id=user_id,
        command="/privacy",
        module="start"
    )
    
    await message.answer(
        PRIVACY_POLICY_TEXT,
        reply_markup=get_back_from_privacy_keyboard()
    )


@router.callback_query(F.data == "privacy_policy")
async def show_privacy_policy(callback: CallbackQuery):
    """Show privacy policy from button"""
    user_id = callback.from_user.id
    db = Database.get_db()
    
    # Log button click
    await log_button_click(
        db=db,
        user_id=user_id,
        button_data="privacy_policy",
        module="start"
    )
    
    await callback.message.edit_text(
        PRIVACY_POLICY_TEXT,
        reply_markup=get_back_from_privacy_keyboard()
    )
    await callback.answer()


@router.message(Command("export_history"))
async def cmd_export_history(message: Message):
    """Export user's activity history"""
    user_id = message.from_user.id
    db = Database.get_db()
    
    # Log command
    await log_command(
        db=db,
        user_id=user_id,
        command="/export_history",
        module="start"
    )
    
    await message.answer("📊 Generating your activity export...")
    
    try:
        # Get user's search logs
        logs = await db.search_logs.find(
            {"telegram_id": user_id}
        ).sort("timestamp", -1).limit(1000).to_list(length=1000)
        
        # Get user profile
        user = await db.users.find_one({"telegram_id": user_id})
        
        # Prepare export data
        export_data = {
            "user_profile": {
                "telegram_id": user_id,
                "username": message.from_user.username,
                "first_name": message.from_user.first_name,
                "tier": user.get("tier", "free") if user else "free",
                "join_date": user.get("join_date").isoformat() if user and user.get("join_date") else None,
                "total_searches": user.get("total_searches", 0) if user else 0,
                "total_commands": user.get("total_commands", 0) if user else 0,
                "modules_used": user.get("modules_used", []) if user else []
            },
            "activity_logs": [
                {
                    "event_type": log.get("event_type"),
                    "query_text": log.get("query_text"),
                    "module_name": log.get("module_name"),
                    "timestamp": log.get("timestamp").isoformat() if log.get("timestamp") else None,
                    "metadata": log.get("metadata", {})
                }
                for log in logs
            ],
            "export_date": datetime.utcnow().isoformat(),
            "total_logs": len(logs)
        }
        
        # Convert to JSON
        json_export = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Send as file
        from io import BytesIO
        file_buffer = BytesIO(json_export.encode('utf-8'))
        file_buffer.name = f"everythinginbot_export_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}.json"
        
        await message.answer_document(
            document=file_buffer,
            caption=f"✅ <b>Your Activity Export</b>\n\n📊 Total logs: {len(logs)}\n📅 Export date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        )
        
        # Log the export action
        await log_action(
            db=db,
            user_id=user_id,
            action="export_history",
            module="start",
            metadata={"logs_exported": len(logs)}
        )
        
    except Exception as e:
        await message.answer(f"❌ Error generating export: {str(e)}")
