"""
Legal Disclaimers
Privacy notices and legal warnings for sensitive modules
"""

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ============================================
# OSINT TOOLS DISCLAIMER
# ============================================

OSINT_DISCLAIMER_TEXT = """
⚠️ <b>OSINT Tools - Legal Disclaimer</b>

<b>IMPORTANT LEGAL NOTICE:</b>

By using these OSINT (Open Source Intelligence) tools, you agree to the following terms:

<b>✅ Permitted Uses:</b>
• Personal security research
• Educational purposes
• Legitimate cybersecurity work
• Authorized penetration testing
• Public information gathering

<b>❌ Prohibited Uses:</b>
• Harassment or stalking
• Unauthorized access attempts
• Violating privacy laws
• Illegal surveillance
• Any malicious activities

<b>🔒 Privacy & Data Protection:</b>
• We do NOT store your queries
• All searches are encrypted
• We comply with GDPR/privacy laws
• Results are from public sources only

<b>⚖️ Legal Responsibility:</b>
• You are solely responsible for your actions
• Misuse may result in legal consequences
• We are not liable for misuse of these tools
• Use must comply with local laws

<b>📋 Data Sources:</b>
• WHOIS databases (public)
• DNS records (public)
• IP geolocation (public)
• Username searches (public platforms)

<b>By clicking "I Agree", you confirm that you:</b>
1. Will use these tools legally and ethically
2. Understand the legal implications
3. Accept full responsibility for your actions
4. Will not use for malicious purposes

<i>Last updated: February 2026</i>
"""


def get_osint_disclaimer_keyboard():
    """Get OSINT disclaimer keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ I Agree - Continue", callback_data="osint_agree"),
        InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")
    )
    return builder.as_markup()


# ============================================
# BREACH CHECK DISCLAIMER
# ============================================

BREACH_DISCLAIMER_TEXT = """
🔒 <b>Breach Check - Privacy & Security Notice</b>

<b>How This Tool Works:</b>

<b>1. Data Processing:</b>
• Your email is hashed using SHA-1 before checking
• We NEVER store your original email address
• Hash is sent to HaveIBeenPwned API
• Results are returned to you only

<b>2. What We Check:</b>
• Public data breach databases
• Known compromised credentials
• Leaked password databases
• Historical security incidents

<b>3. Privacy Guarantees:</b>
✅ No email storage
✅ No logging of queries
✅ Encrypted transmission
✅ Anonymous checking
✅ GDPR compliant

<b>4. Data Sources:</b>
• HaveIBeenPwned (Troy Hunt)
• Public breach databases
• Security research databases

<b>5. What Results Mean:</b>
• <b>Found</b>: Your email appears in known breaches
• <b>Not Found</b>: No breaches detected (good!)
• <b>Breaches Listed</b>: Which services were compromised

<b>6. Recommended Actions if Found:</b>
1. Change passwords immediately
2. Enable 2FA on all accounts
3. Use unique passwords per service
4. Monitor for suspicious activity
5. Consider password manager

<b>🔐 Your Security is Our Priority</b>

We take your privacy seriously:
• Zero data retention
• Secure API communication
• No third-party sharing
• Full transparency

<b>⚖️ Legal Notice:</b>
This tool is for security awareness only. We are not responsible for how you use the information provided.

<i>Powered by HaveIBeenPwned API</i>
"""


def get_breach_disclaimer_keyboard():
    """Get breach check disclaimer keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ I Understand - Check Email", callback_data="breach_agree"),
        InlineKeyboardButton(text="📖 Learn More", url="https://haveibeenpwned.com/"),
        InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")
    )
    return builder.as_markup()


# ============================================
# GENERAL DATA POLICY
# ============================================

DATA_USAGE_POLICY = """
📋 <b>Data Usage Policy</b>

<b>What Data We Collect:</b>
• Telegram User ID (for identification)
• Search queries (for logging)
• Module usage statistics
• Timestamps of actions
• IP address (for security)

<b>What We DON'T Collect:</b>
❌ Personal messages
❌ Email addresses (except for breach check, hashed only)
❌ Passwords
❌ Payment information
❌ Location data

<b>How We Use Data:</b>
• Improve bot functionality
• Prevent abuse and spam
• Generate usage statistics
• Security monitoring
• Comply with legal requirements

<b>Data Retention:</b>
• Logs: 180 days (auto-deleted)
• User profiles: Until account deletion
• Search history: 180 days
• Analytics: Aggregated, anonymous

<b>Your Rights:</b>
✅ Request data export (/export_history)
✅ Request data deletion
✅ Opt-out of analytics
✅ Access your data

<b>Security Measures:</b>
🔒 Encrypted database
🔒 Secure API endpoints
🔒 Regular security audits
🔒 Access controls

<b>Contact:</b>
For privacy concerns or data requests, contact the bot administrator.

<i>Last updated: February 2026</i>
"""


# ============================================
# AI DISCLAIMER
# ============================================

AI_DISCLAIMER_TEXT = """
🤖 <b>AI Tools - Important Notice</b>

<b>About AI-Generated Content:</b>

<b>⚠️ Accuracy:</b>
• AI responses may contain errors
• Always verify critical information
• Not a substitute for professional advice
• May produce outdated information

<b>🎨 Image Generation:</b>
• Images are AI-generated
• May not be 100% accurate
• For creative/educational use
• Respect copyright and usage rights

<b>💬 Text Generation:</b>
• Responses are generated by AI models
• May reflect biases in training data
• Should not be used for:
  - Medical advice
  - Legal advice
  - Financial decisions
  - Critical safety decisions

<b>🔒 Privacy:</b>
• Your prompts may be logged
• Do not share sensitive information
• AI providers may use data for improvement

<b>⚖️ Responsibility:</b>
• You are responsible for how you use AI outputs
• Verify information before acting on it
• Use ethically and legally

<b>Models Used:</b>
• GPT-4o (OpenAI)
• Claude (Anthropic)
• Gemini (Google)
• DALL-E (OpenAI)

<i>AI is a tool, not a replacement for human judgment.</i>
"""


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_disclaimer_for_module(module_name: str) -> tuple[str, any]:
    """
    Get disclaimer text and keyboard for a module
    
    Args:
        module_name: Module identifier
        
    Returns:
        Tuple of (disclaimer_text, keyboard)
    """
    disclaimers = {
        'osint': (OSINT_DISCLAIMER_TEXT, get_osint_disclaimer_keyboard()),
        'breach': (BREACH_DISCLAIMER_TEXT, get_breach_disclaimer_keyboard()),
        'ai': (AI_DISCLAIMER_TEXT, None),
        'data_policy': (DATA_USAGE_POLICY, None)
    }
    
    return disclaimers.get(module_name, (None, None))
