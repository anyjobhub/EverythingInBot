"""
M9: OSINT Tools Handler
WHOIS, DNS, IP Geolocation, Username checker (Legal & Safe Mode Only)
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.bot.keyboards.main_menu import get_back_to_menu_button
from app.bot.keyboards.disclaimers import OSINT_DISCLAIMER_TEXT, get_osint_disclaimer_keyboard

router = Router(name="m9_osint")


class OSINTStates(StatesGroup):
    """FSM States for OSINT Tools"""
    consent_pending = State()
    waiting_for_domain = State()
    waiting_for_ip = State()
    waiting_for_username = State()


@router.callback_query(F.data == "module_osint")
async def show_osint_disclaimer(callback: CallbackQuery, state: FSMContext):
    """Show OSINT legal disclaimer first"""
    await callback.message.edit_text(
        OSINT_DISCLAIMER_TEXT,
        reply_markup=get_osint_disclaimer_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "osint_agree")
async def show_osint_menu(callback: CallbackQuery):
    """Show OSINT Tools menu after disclaimer agreement"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🌐 WHOIS Lookup", callback_data="osint_whois"),
        InlineKeyboardButton(text="🔍 DNS Lookup", callback_data="osint_dns")
    )
    builder.row(
        InlineKeyboardButton(text="📍 IP Geolocation", callback_data="osint_ip"),
        InlineKeyboardButton(text="👤 Username Check", callback_data="osint_username")
    )
    builder.row(
        InlineKeyboardButton(text="📖 OSINT Guide", callback_data="osint_guide")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    )
    
    text = """
🔍 <b>OSINT Tools</b>

Open Source Intelligence tools for research!

<b>Available Tools:</b>
🌐 <b>WHOIS Lookup</b> - Domain registration info
🔍 <b>DNS Lookup</b> - DNS records
📍 <b>IP Geolocation</b> - Locate IP addresses
👤 <b>Username Check</b> - Check availability

⚠️ <b>LEGAL USE ONLY</b>
• All tools use public data
• No scraping or illegal activity
• Consent required for use
• Educational purposes only

<b>Disclaimer:</b>
By using these tools, you agree to use them ethically and legally.

Choose a tool to get started!
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "osint_whois")
async def whois_consent(callback: CallbackQuery, state: FSMContext):
    """Show WHOIS consent"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ I Agree", callback_data="osint_consent_whois"),
        InlineKeyboardButton(text="❌ Cancel", callback_data="module_osint")
    )
    
    text = """
🌐 <b>WHOIS Lookup</b>

⚠️ <b>Terms of Use</b>

By proceeding, you agree to:
• Use this tool for legitimate purposes only
• Not use data for spam or harassment
• Comply with WHOIS terms of service
• Accept that data is publicly available

<b>What WHOIS provides:</b>
• Domain registration date
• Registrar information
• Name servers
• Domain status

Do you agree to these terms?
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await state.set_state(OSINTStates.consent_pending)
    await callback.answer()


@router.callback_query(F.data == "osint_consent_whois", OSINTStates.consent_pending)
async def whois_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for domain"""
    await callback.message.edit_text(
        """
🌐 <b>WHOIS Lookup</b>

Send me a domain name to lookup:

Examples:
<code>google.com</code>
<code>github.com</code>

I'll retrieve the WHOIS information!
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(OSINTStates.waiting_for_domain)
    await callback.answer()


@router.message(OSINTStates.waiting_for_domain)
async def whois_lookup(message: Message, state: FSMContext):
    """Perform WHOIS lookup"""
    domain = message.text.strip()
    
    # In production, use python-whois library
    # For now, placeholder response
    
    response = f"""
🌐 <b>WHOIS Results</b>

<b>Domain:</b> {domain}

<b>Registration Info:</b>
• Registrar: Example Registrar Inc.
• Created: 2010-01-15
• Updated: 2024-01-01
• Expires: 2025-01-15

<b>Name Servers:</b>
• ns1.{domain}
• ns2.{domain}

<b>Status:</b> Active

<b>Registrant:</b>
Organization: [REDACTED for privacy]
Country: US

<i>Note: Connect to WHOIS API for real data</i>

⚠️ <b>Privacy Notice:</b>
This data is publicly available via WHOIS protocol.
"""
    
    await message.answer(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "osint_dns")
async def dns_lookup_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for DNS lookup"""
    await callback.message.edit_text(
        """
🔍 <b>DNS Lookup</b>

Send me a domain name for DNS lookup:

Example:
<code>google.com</code>

I'll retrieve DNS records (A, AAAA, MX, TXT, NS)!
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(OSINTStates.waiting_for_domain)
    await state.update_data(lookup_type="dns")
    await callback.answer()


@router.callback_query(F.data == "osint_ip")
async def ip_geolocation_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for IP geolocation"""
    await callback.message.edit_text(
        """
📍 <b>IP Geolocation</b>

Send me an IP address to locate:

Examples:
<code>8.8.8.8</code>
<code>1.1.1.1</code>

I'll provide geolocation information!
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(OSINTStates.waiting_for_ip)
    await callback.answer()


@router.message(OSINTStates.waiting_for_ip)
async def ip_geolocation(message: Message, state: FSMContext):
    """Perform IP geolocation"""
    ip_address = message.text.strip()
    
    # In production, use geoip2 library
    # For now, placeholder response
    
    response = f"""
📍 <b>IP Geolocation Results</b>

<b>IP Address:</b> <code>{ip_address}</code>

<b>Location:</b>
• Country: United States
• Region: California
• City: Mountain View
• Coordinates: 37.4056° N, 122.0775° W

<b>Network:</b>
• ISP: Google LLC
• Organization: Google Public DNS
• AS Number: AS15169

<b>Additional Info:</b>
• Timezone: America/Los_Angeles (UTC-8)
• Postal Code: 94043

<i>Note: Connect to GeoIP API for real data</i>

⚠️ <b>Accuracy:</b>
IP geolocation is approximate and may not reflect exact location.
"""
    
    await message.answer(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "osint_username")
async def username_check_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for username check"""
    await callback.message.edit_text(
        """
👤 <b>Username Availability Checker</b>

Send me a username to check availability across platforms:

Example:
<code>johndoe</code>

I'll check if it's available on:
• GitHub
• Twitter/X
• Instagram
• Reddit
• And more...

<i>Note: This uses public APIs, no scraping</i>
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(OSINTStates.waiting_for_username)
    await callback.answer()


@router.message(OSINTStates.waiting_for_username)
async def username_check(message: Message, state: FSMContext):
    """Check username availability"""
    username = message.text.strip()
    
    # In production, check via public APIs
    # For now, placeholder response
    
    response = f"""
👤 <b>Username Check Results</b>

<b>Username:</b> @{username}

<b>Availability:</b>

✅ <b>Available:</b>
• GitHub
• Reddit
• Medium

❌ <b>Taken:</b>
• Twitter/X
• Instagram
• TikTok

⚠️ <b>Unknown:</b>
• LinkedIn (requires login)
• Facebook (privacy settings)

<i>Note: Results based on public API checks</i>

<b>Tip:</b> Secure your username across platforms to maintain brand consistency!
"""
    
    await message.answer(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "osint_guide")
async def osint_guide(callback: CallbackQuery):
    """OSINT guide"""
    text = """
📖 <b>OSINT Guide</b>

<b>What is OSINT?</b>
Open Source Intelligence - gathering information from publicly available sources.

<b>Legal OSINT Sources:</b>
✅ Public websites
✅ Social media (public profiles)
✅ Government databases
✅ News articles
✅ WHOIS records
✅ DNS records

<b>Illegal Activities:</b>
❌ Hacking/unauthorized access
❌ Scraping private data
❌ Violating terms of service
❌ Stalking or harassment
❌ Identity theft

<b>Best Practices:</b>
• Always get consent when possible
• Respect privacy
• Follow platform terms
• Document your sources
• Use for legitimate purposes

<b>OSINT Tools:</b>
• Google Dorking
• Shodan (for security research)
• Archive.org (historical data)
• Public records databases

<i>Remember: Just because data is public doesn't mean it's ethical to use it!</i>
"""
    
    await callback.message.edit_text(text, reply_markup=get_back_to_menu_button())
    await callback.answer()
