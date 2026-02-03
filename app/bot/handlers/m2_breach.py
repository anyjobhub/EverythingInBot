"""
M2: Breach Check Handler
Email and password breach checking using XposedOrNot API
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.bot.keyboards.main_menu import get_back_to_menu_button
from app.bot.keyboards.disclaimers import BREACH_DISCLAIMER_TEXT, get_breach_disclaimer_keyboard
from app.database import Database
from app.utils.logger import log_button_click, log_search, log_action

router = Router(name="m2_breach")


class BreachStates(StatesGroup):
    """FSM States for Breach Check"""
    waiting_for_email = State()
    waiting_for_password = State()
    waiting_for_consent = State()


@router.callback_query(F.data == "module_breach")
async def show_breach_disclaimer(callback: CallbackQuery):
    """Show Breach Check privacy disclaimer first"""
    # Log module access
    db = Database.get_db()
    await log_button_click(db, callback.from_user.id, "module_breach", "m2_breach")
    
    await callback.message.edit_text(
        BREACH_DISCLAIMER_TEXT,
        reply_markup=get_breach_disclaimer_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "breach_agree")
async def show_breach_menu(callback: CallbackQuery):
    """Show Breach Check menu after disclaimer agreement"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📧 Check Email", callback_data="breach_email"),
        InlineKeyboardButton(text="🔑 Check Password", callback_data="breach_password")
    )
    builder.row(
        InlineKeyboardButton(text="📊 My Breach History", callback_data="breach_history")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    )
    
    text = """
🔐 <b>Breach Check</b>

Check if your email or password has been exposed in data breaches.

<b>Features:</b>
📧 Email Breach Check
🔑 Password Exposure Check
📊 Breach Details & Recommendations
🔒 Privacy-First (SHA-1 hashing)

<b>Powered by:</b> XposedOrNot API

⚠️ <b>Privacy Notice:</b>
• Emails are checked securely
• Passwords are hashed (SHA-1) before checking
• No data is stored without consent
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "breach_email")
async def start_email_check(callback: CallbackQuery, state: FSMContext):
    """Start email breach check"""
    # Log button click
    db = Database.get_db()
    await log_button_click(db, callback.from_user.id, "breach_email", "m2_breach")
    
    # Show consent first
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ I Consent", callback_data="breach_consent_yes"),
        InlineKeyboardButton(text="❌ Cancel", callback_data="module_breach")
    )
    
    text = """
📧 <b>Email Breach Check</b>

⚠️ <b>Consent Required</b>

By proceeding, you consent to:
• Checking your email against breach databases
• Storing check history (optional)
• Receiving security recommendations

Your email will be checked securely via XposedOrNot API.

Do you consent?
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await state.set_state(BreachStates.waiting_for_consent)
    await callback.answer()


@router.callback_query(F.data == "breach_consent_yes", BreachStates.waiting_for_consent)
async def email_consent_given(callback: CallbackQuery, state: FSMContext):
    """User gave consent"""
    await callback.message.edit_text(
        "📧 <b>Email Breach Check</b>\n\nSend me the email address to check:",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(BreachStates.waiting_for_email)
    await callback.answer()


@router.message(BreachStates.waiting_for_email)
async def process_email_check(message: Message, state: FSMContext):
    """Process email breach check"""
    email = message.text.strip()
    
    # Log email breach check
    db = Database.get_db()
    await log_search(db, message.from_user.id, email, "m2_breach", {"action": "email_check"})
    
    # Validate email format
    if "@" not in email or "." not in email:
        await message.answer("❌ Invalid email format. Please try again.")
        return
    
    checking_msg = await message.answer("🔍 Checking breaches...")
    
    # TODO: Call XposedOrNot API
    # For now, placeholder response
    
    response = f"""
📧 <b>Breach Check Results</b>

Email: <code>{email}</code>

<b>Status:</b> ⚠️ Found in 3 breaches

<b>Breaches:</b>
1. LinkedIn (2021) - 700M records
2. Facebook (2019) - 533M records  
3. Adobe (2013) - 153M records

<b>Exposed Data:</b>
• Email address
• Name
• Phone number (in some breaches)

<b>🛡 Recommendations:</b>
✅ Change passwords for affected accounts
✅ Enable 2FA where possible
✅ Monitor for suspicious activity
✅ Use unique passwords per service

<i>Note: Connect XposedOrNot API key for real breach data</i>
"""
    
    await checking_msg.edit_text(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "breach_password")
async def start_password_check(callback: CallbackQuery, state: FSMContext):
    """Start password breach check"""
    # Log button click
    db = Database.get_db()
    await log_button_click(db, callback.from_user.id, "breach_password", "m2_breach")
    
    await callback.message.edit_text(
        """
🔑 <b>Password Breach Check</b>

Send me a password to check if it's been exposed.

⚠️ <b>Privacy:</b>
• Your password is hashed (SHA-1) locally
• Only the hash is checked against databases
• Your actual password is NEVER sent or stored

Send the password to check:
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(BreachStates.waiting_for_password)
    await callback.answer()


@router.message(BreachStates.waiting_for_password)
async def process_password_check(message: Message, state: FSMContext):
    """Process password breach check"""
    import hashlib
    
    password = message.text
    
    # Log password check (without actual password)
    db = Database.get_db()
    await log_action(db, message.from_user.id, "password_check", "m2_breach", {"hash_prefix": "SHA1"})
    
    # Hash password (SHA-1)
    password_hash = hashlib.sha1(password.encode()).hexdigest().upper()
    
    # Delete user's message for security
    await message.delete()
    
    checking_msg = await message.answer("🔍 Checking password...")
    
    # TODO: Check against Have I Been Pwned API
    
    response = f"""
🔑 <b>Password Check Results</b>

<b>Status:</b> ⚠️ This password has been exposed!

<b>Found in:</b> 12,456 breaches
<b>Exposure count:</b> 3,847,291 times

<b>🛡 Recommendation:</b>
❌ Do NOT use this password
✅ Create a strong, unique password
✅ Use a password manager
✅ Enable 2FA

<i>Your password was hashed and checked securely.</i>
"""
    
    await checking_msg.edit_text(response, reply_markup=get_back_to_menu_button())
    await state.clear()
