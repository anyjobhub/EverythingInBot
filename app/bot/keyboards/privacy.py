"""
Privacy policy keyboard and handler
"""

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_privacy_keyboard():
    """Get privacy policy keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🔒 Security & Data Policy",
            callback_data="privacy_policy"
        )
    )
    
    return builder.as_markup()


def get_back_from_privacy_keyboard():
    """Get back button from privacy policy"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data="main_menu")
    )
    
    return builder.as_markup()


# Privacy policy text
PRIVACY_POLICY_TEXT = """
🔒 <b>Security & Data Policy</b>

To protect the platform, detect abuse, and maintain system integrity, this bot securely logs the following information:

<b>Data We Collect:</b>
• User profile information (name, username, Telegram ID)
• Search history and queries
• Module usage patterns
• Command history
• Timestamps of all interactions
• Device information (IP address, user agent)
• Session data

<b>How We Use This Data:</b>
✅ Detect and prevent abuse
✅ Improve bot performance
✅ Provide personalized experience
✅ Generate usage analytics
✅ Ensure platform security

<b>Data Retention:</b>
• Logs are kept for 180 days
• Automatic cleanup after retention period
• You can export your data anytime

<b>Your Rights:</b>
• View your activity logs
• Export your data
• Request data deletion

<b>Data Protection:</b>
🔐 Your data is encrypted
🔐 NOT sold to third parties
🔐 NOT shared externally
🔐 Stored securely on MongoDB Atlas

<b>Commands:</b>
/export_history - Export your data
/privacy - View this policy

By continuing to use this bot, you acknowledge and accept this data policy.
"""

# Security disclaimer for /start
SECURITY_DISCLAIMER = """
⚠️ <b>Security Notice</b>

For security and abuse-prevention purposes, this bot stores:
• User activity
• Search history
• Module usage logs

Your data is secure and never shared. See /privacy for details.
"""
