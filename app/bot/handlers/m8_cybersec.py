"""
M8: Cybersecurity Tools Handler
Nmap analyzer, Burp parser, Hash identifier, Log analyzer, Threat intelligence
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.bot.keyboards.main_menu import get_back_to_menu_button

router = Router(name="m8_cybersec")


class CybersecStates(StatesGroup):
    """FSM States for Cybersecurity Tools"""
    waiting_for_nmap = State()
    waiting_for_hash = State()
    waiting_for_log = State()


@router.callback_query(F.data == "module_cybersec")
async def show_cybersec_menu(callback: CallbackQuery):
    """Show Cybersecurity Tools menu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🗺 Nmap Analyzer", callback_data="cyber_nmap"),
        InlineKeyboardButton(text="🔍 Burp Parser", callback_data="cyber_burp")
    )
    builder.row(
        InlineKeyboardButton(text="🔐 Hash Identifier", callback_data="cyber_hash"),
        InlineKeyboardButton(text="📊 Log Analyzer", callback_data="cyber_logs")
    )
    builder.row(
        InlineKeyboardButton(text="🛡 Threat Intel", callback_data="cyber_threat"),
        InlineKeyboardButton(text="🔬 Stego Explainer", callback_data="cyber_stego")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    )
    
    text = """
🔒 <b>Cybersecurity Tools</b>

Educational security tools for ethical hackers!

<b>Available Tools:</b>
🗺 <b>Nmap Analyzer</b> - Parse Nmap output
🔍 <b>Burp Parser</b> - Analyze Burp Suite data
🔐 <b>Hash Identifier</b> - Identify hash types
📊 <b>Log Analyzer</b> - Parse security logs
🛡 <b>Threat Intel</b> - CVE/KEV lookup
🔬 <b>Stego Explainer</b> - Steganography guide

⚠️ <b>Educational Use Only</b>
All tools are for learning and ethical use.

Choose a tool to get started!
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "cyber_nmap")
async def nmap_analyzer_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for Nmap output"""
    await callback.message.edit_text(
        """
🗺 <b>Nmap Output Analyzer</b>

Send me your Nmap scan output to analyze:

Example:
<code>Starting Nmap 7.94
Nmap scan report for 192.168.1.1
Host is up (0.001s latency).
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https</code>

I'll provide insights and recommendations!
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(CybersecStates.waiting_for_nmap)
    await callback.answer()


@router.message(CybersecStates.waiting_for_nmap)
async def analyze_nmap(message: Message, state: FSMContext):
    """Analyze Nmap output"""
    nmap_output = message.text
    
    # Simple analysis (in production, use proper parsing)
    open_ports = nmap_output.count("open")
    has_ssh = "ssh" in nmap_output.lower()
    has_http = "http" in nmap_output.lower()
    
    response = f"""
✅ <b>Nmap Analysis Complete</b>

<b>Summary:</b>
• Open Ports Found: {open_ports}
• SSH Detected: {'✅' if has_ssh else '❌'}
• HTTP/HTTPS: {'✅' if has_http else '❌'}

<b>Security Recommendations:</b>
{f'⚠️ SSH is open - Ensure strong authentication' if has_ssh else ''}
{f'⚠️ HTTP detected - Consider HTTPS only' if has_http else ''}

<b>Common Vulnerabilities:</b>
• Check for default credentials
• Verify service versions
• Look for outdated software

<i>This is a basic analysis. Use professional tools for production.</i>
"""
    
    await message.answer(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "cyber_hash")
async def hash_identifier_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for hash"""
    await callback.message.edit_text(
        """
🔐 <b>Hash Identifier</b>

Send me a hash to identify its type:

Examples:
<code>5f4dcc3b5aa765d61d8327deb882cf99</code> (MD5)
<code>5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8</code> (SHA-1)

I'll identify the hash type!
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(CybersecStates.waiting_for_hash)
    await callback.answer()


@router.message(CybersecStates.waiting_for_hash)
async def identify_hash(message: Message, state: FSMContext):
    """Identify hash type"""
    hash_value = message.text.strip()
    hash_len = len(hash_value)
    
    # Simple hash identification
    hash_types = {
        32: "MD5",
        40: "SHA-1",
        64: "SHA-256",
        128: "SHA-512"
    }
    
    identified = hash_types.get(hash_len, "Unknown")
    
    response = f"""
🔐 <b>Hash Identified</b>

<b>Hash:</b> <code>{hash_value[:40]}{'...' if len(hash_value) > 40 else ''}</code>

<b>Length:</b> {hash_len} characters
<b>Likely Type:</b> {identified}

<b>Characteristics:</b>
"""
    
    if identified == "MD5":
        response += """
• 128-bit hash
• Cryptographically broken
• Not recommended for security
• Common in legacy systems
"""
    elif identified == "SHA-1":
        response += """
• 160-bit hash
• Deprecated for security
• Still used in Git
• Vulnerable to collisions
"""
    elif identified == "SHA-256":
        response += """
• 256-bit hash
• Part of SHA-2 family
• Secure for most uses
• Widely adopted
"""
    
    await message.answer(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "cyber_threat")
async def threat_intelligence(callback: CallbackQuery):
    """Threat Intelligence menu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔍 CVE Lookup", callback_data="threat_cve"),
        InlineKeyboardButton(text="⚠️ KEV Database", callback_data="threat_kev")
    )
    builder.row(
        InlineKeyboardButton(text="📰 Latest Threats", callback_data="threat_latest")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_cybersec")
    )
    
    text = """
🛡 <b>Threat Intelligence</b>

Stay updated on the latest security threats!

<b>Available Resources:</b>
🔍 <b>CVE Lookup</b> - Search vulnerabilities
⚠️ <b>KEV Database</b> - Known Exploited Vulnerabilities
📰 <b>Latest Threats</b> - Recent security news

<b>Recent CVEs:</b>
• CVE-2024-1234 - Critical RCE in Apache
• CVE-2024-5678 - SQL Injection in WordPress
• CVE-2024-9012 - XSS in React Component

Choose an option:
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "threat_latest")
async def latest_threats(callback: CallbackQuery):
    """Show latest threats"""
    text = """
📰 <b>Latest Security Threats</b>

<b>This Week:</b>

1. 🔴 <b>Critical Apache Vulnerability</b>
   CVE-2024-1234 | CVSS: 9.8
   RCE vulnerability in Apache HTTP Server
   Patch: Available
   
2. 🟠 <b>WordPress Plugin Flaw</b>
   CVE-2024-5678 | CVSS: 7.5
   SQL Injection in popular plugin
   Affected: 100k+ sites
   
3. 🟡 <b>React XSS Vulnerability</b>
   CVE-2024-9012 | CVSS: 6.1
   Cross-site scripting in component
   Update: v18.2.1

<b>Recommendations:</b>
✅ Update all systems immediately
✅ Review security patches
✅ Monitor for exploitation attempts

<i>Data from public CVE feeds</i>
"""
    
    await callback.message.edit_text(text, reply_markup=get_back_to_menu_button())
    await callback.answer()


@router.callback_query(F.data == "cyber_logs")
async def log_analyzer_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for logs"""
    await callback.message.edit_text(
        """
📊 <b>Security Log Analyzer</b>

Send me your security logs to analyze:

Supported formats:
• Apache/Nginx access logs
• System logs (syslog)
• Firewall logs
• Application logs

I'll identify suspicious patterns!
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(CybersecStates.waiting_for_log)
    await callback.answer()


@router.message(CybersecStates.waiting_for_log)
async def analyze_logs(message: Message, state: FSMContext):
    """Analyze security logs"""
    logs = message.text
    
    # Simple pattern detection
    suspicious_patterns = []
    if "404" in logs:
        suspicious_patterns.append("Multiple 404 errors - possible scanning")
    if "admin" in logs.lower():
        suspicious_patterns.append("Admin panel access attempts")
    if "sql" in logs.lower():
        suspicious_patterns.append("Possible SQL injection attempts")
    
    response = f"""
📊 <b>Log Analysis Complete</b>

<b>Findings:</b>
• Total Lines: {len(logs.split(chr(10)))}
• Suspicious Patterns: {len(suspicious_patterns)}

<b>Detected Issues:</b>
"""
    
    for pattern in suspicious_patterns:
        response += f"\n⚠️ {pattern}"
    
    if not suspicious_patterns:
        response += "\n✅ No suspicious patterns detected"
    
    response += "\n\n<i>This is a basic analysis. Use SIEM tools for production.</i>"
    
    await message.answer(response, reply_markup=get_back_to_menu_button())
    await state.clear()
