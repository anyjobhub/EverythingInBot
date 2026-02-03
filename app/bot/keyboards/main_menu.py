"""
Main Menu Keyboard
Inline keyboard with all 10 modules
"""

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Create main menu keyboard with all 10 modules
    """
    builder = InlineKeyboardBuilder()
    
    # Row 1: AI & Security
    builder.row(
        InlineKeyboardButton(text="🤖 AI Engine", callback_data="module_ai"),
        InlineKeyboardButton(text="🔐 Breach Check", callback_data="module_breach")
    )
    
    # Row 2: Learning & Jobs
    builder.row(
        InlineKeyboardButton(text="📚 Courses", callback_data="module_courses"),
        InlineKeyboardButton(text="💼 Jobs", callback_data="module_jobs")
    )
    
    # Row 3: Tools & Productivity
    builder.row(
        InlineKeyboardButton(text="🛠 Tools", callback_data="module_tools"),
        InlineKeyboardButton(text="✅ Productivity", callback_data="module_productivity")
    )
    
    # Row 4: Developer & Cybersecurity
    builder.row(
        InlineKeyboardButton(text="👨‍💻 Dev Tools", callback_data="module_devtools"),
        InlineKeyboardButton(text="🔒 Cybersec", callback_data="module_cybersec")
    )
    
    # Row 5: OSINT & Fun
    builder.row(
        InlineKeyboardButton(text="🔍 OSINT", callback_data="module_osint"),
        InlineKeyboardButton(text="🎮 Fun", callback_data="module_fun")
    )
    
    # Row 6: Profile & Upgrade
    builder.row(
        InlineKeyboardButton(text="👤 Profile", callback_data="show_profile"),
        InlineKeyboardButton(text="⭐ Upgrade", callback_data="upgrade_pro")
    )
    
    return builder.as_markup()


def get_back_to_menu_button() -> InlineKeyboardMarkup:
    """Simple back to menu button"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu"))
    return builder.as_markup()
