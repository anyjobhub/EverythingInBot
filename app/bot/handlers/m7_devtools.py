"""
M7: Developer Tools Handler
JSON formatter, JWT decoder, Regex generator, API tester, Cron builder, Cheat sheets
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.bot.keyboards.main_menu import get_back_to_menu_button
import json
import base64

router = Router(name="m7_devtools")


class DevToolsStates(StatesGroup):
    """FSM States for Developer Tools"""
    waiting_for_json = State()
    waiting_for_jwt = State()
    waiting_for_base64 = State()
    waiting_for_regex = State()


@router.callback_query(F.data == "module_devtools")
async def show_devtools_menu(callback: CallbackQuery):
    """Show Developer Tools menu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📋 JSON Tools", callback_data="dev_json"),
        InlineKeyboardButton(text="🔐 JWT Decoder", callback_data="dev_jwt")
    )
    builder.row(
        InlineKeyboardButton(text="🔤 Base64", callback_data="dev_base64"),
        InlineKeyboardButton(text="🔍 Regex", callback_data="dev_regex")
    )
    builder.row(
        InlineKeyboardButton(text="🌐 API Tester", callback_data="dev_api"),
        InlineKeyboardButton(text="⏰ Cron Builder", callback_data="dev_cron")
    )
    builder.row(
        InlineKeyboardButton(text="📚 Cheat Sheets", callback_data="dev_cheatsheets")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    )
    
    text = """
👨‍💻 <b>Developer Tools</b>

Essential tools for developers!

<b>Available Tools:</b>
📋 <b>JSON Tools</b> - Format, validate, minify
🔐 <b>JWT Decoder</b> - Decode JWT tokens
🔤 <b>Base64</b> - Encode/decode
🔍 <b>Regex</b> - Test & generate patterns
🌐 <b>API Tester</b> - Test REST APIs
⏰ <b>Cron Builder</b> - Generate cron expressions
📚 <b>Cheat Sheets</b> - Git, Docker, K8s, Linux

Choose a tool to get started!
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "dev_json")
async def json_tools_menu(callback: CallbackQuery):
    """JSON tools submenu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✨ Format JSON", callback_data="json_format"),
        InlineKeyboardButton(text="✅ Validate JSON", callback_data="json_validate")
    )
    builder.row(
        InlineKeyboardButton(text="🗜 Minify JSON", callback_data="json_minify")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_devtools")
    )
    
    await callback.message.edit_text(
        "📋 <b>JSON Tools</b>\n\nSelect an operation:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "json_format")
async def json_format_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for JSON to format"""
    await callback.message.edit_text(
        """
✨ <b>JSON Formatter</b>

Send me your JSON to format:

Example:
<code>{"name":"John","age":30,"city":"NYC"}</code>

I'll format it beautifully!
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(DevToolsStates.waiting_for_json)
    await callback.answer()


@router.message(DevToolsStates.waiting_for_json)
async def format_json(message: Message, state: FSMContext):
    """Format JSON"""
    try:
        # Parse and format JSON
        json_data = json.loads(message.text)
        formatted = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        response = f"""
✅ <b>Formatted JSON:</b>

<code>{formatted}</code>

<b>Stats:</b>
• Valid JSON: ✅
• Objects: {str(json_data).count('{')}
• Arrays: {str(json_data).count('[')}
"""
        
    except json.JSONDecodeError as e:
        response = f"""
❌ <b>Invalid JSON</b>

<b>Error:</b> {str(e)}

Please check your JSON syntax and try again.
"""
    
    await message.answer(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "dev_jwt")
async def jwt_decoder_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for JWT token"""
    await callback.message.edit_text(
        """
🔐 <b>JWT Decoder</b>

Send me a JWT token to decode:

Example:
<code>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c</code>

I'll decode the header and payload!
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(DevToolsStates.waiting_for_jwt)
    await callback.answer()


@router.message(DevToolsStates.waiting_for_jwt)
async def decode_jwt(message: Message, state: FSMContext):
    """Decode JWT token"""
    try:
        token = message.text.strip()
        parts = token.split('.')
        
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")
        
        # Decode header and payload (add padding if needed)
        def decode_part(part):
            padding = 4 - len(part) % 4
            if padding != 4:
                part += '=' * padding
            return json.loads(base64.urlsafe_b64decode(part))
        
        header = decode_part(parts[0])
        payload = decode_part(parts[1])
        
        response = f"""
✅ <b>JWT Decoded</b>

<b>Header:</b>
<code>{json.dumps(header, indent=2)}</code>

<b>Payload:</b>
<code>{json.dumps(payload, indent=2)}</code>

<b>Signature:</b> {parts[2][:20]}...

⚠️ <i>Note: Signature not verified</i>
"""
        
    except Exception as e:
        response = f"""
❌ <b>Invalid JWT Token</b>

<b>Error:</b> {str(e)}

Please provide a valid JWT token.
"""
    
    await message.answer(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "dev_base64")
async def base64_tools(callback: CallbackQuery):
    """Base64 encode/decode menu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📤 Encode", callback_data="base64_encode"),
        InlineKeyboardButton(text="📥 Decode", callback_data="base64_decode")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_devtools")
    )
    
    await callback.message.edit_text(
        "🔤 <b>Base64 Tools</b>\n\nSelect an operation:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "base64_encode")
async def base64_encode_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for text to encode"""
    await callback.message.edit_text(
        "📤 <b>Base64 Encode</b>\n\nSend me text to encode:",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(DevToolsStates.waiting_for_base64)
    await state.update_data(operation="encode")
    await callback.answer()


@router.callback_query(F.data == "base64_decode")
async def base64_decode_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for base64 to decode"""
    await callback.message.edit_text(
        "📥 <b>Base64 Decode</b>\n\nSend me base64 string to decode:",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(DevToolsStates.waiting_for_base64)
    await state.update_data(operation="decode")
    await callback.answer()


@router.message(DevToolsStates.waiting_for_base64)
async def process_base64(message: Message, state: FSMContext):
    """Process base64 encode/decode"""
    data = await state.get_data()
    operation = data.get("operation", "encode")
    
    try:
        if operation == "encode":
            result = base64.b64encode(message.text.encode()).decode()
            response = f"✅ <b>Encoded:</b>\n\n<code>{result}</code>"
        else:
            result = base64.b64decode(message.text).decode()
            response = f"✅ <b>Decoded:</b>\n\n<code>{result}</code>"
    except Exception as e:
        response = f"❌ <b>Error:</b> {str(e)}"
    
    await message.answer(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "dev_cron")
async def cron_builder(callback: CallbackQuery):
    """Cron expression builder"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="⏰ Every Hour", callback_data="cron_hourly"),
        InlineKeyboardButton(text="📅 Daily", callback_data="cron_daily")
    )
    builder.row(
        InlineKeyboardButton(text="📆 Weekly", callback_data="cron_weekly"),
        InlineKeyboardButton(text="📊 Monthly", callback_data="cron_monthly")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_devtools")
    )
    
    text = """
⏰ <b>Cron Expression Builder</b>

Generate cron expressions easily!

<b>Common Patterns:</b>
• Every Hour: <code>0 * * * *</code>
• Daily at 9 AM: <code>0 9 * * *</code>
• Weekly (Monday): <code>0 0 * * 1</code>
• Monthly (1st): <code>0 0 1 * *</code>

Select a pattern or send custom expression:
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "dev_cheatsheets")
async def cheatsheets_menu(callback: CallbackQuery):
    """Cheat sheets menu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔧 Git", callback_data="cheat_git"),
        InlineKeyboardButton(text="🐳 Docker", callback_data="cheat_docker")
    )
    builder.row(
        InlineKeyboardButton(text="☸️ Kubernetes", callback_data="cheat_k8s"),
        InlineKeyboardButton(text="🐧 Linux", callback_data="cheat_linux")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_devtools")
    )
    
    await callback.message.edit_text(
        "📚 <b>Developer Cheat Sheets</b>\n\nSelect a topic:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "cheat_git")
async def git_cheatsheet(callback: CallbackQuery):
    """Git cheat sheet"""
    text = """
🔧 <b>Git Cheat Sheet</b>

<b>Basic Commands:</b>
<code>git init</code> - Initialize repo
<code>git clone [url]</code> - Clone repo
<code>git status</code> - Check status
<code>git add .</code> - Stage all changes
<code>git commit -m "msg"</code> - Commit
<code>git push</code> - Push to remote
<code>git pull</code> - Pull from remote

<b>Branching:</b>
<code>git branch</code> - List branches
<code>git branch [name]</code> - Create branch
<code>git checkout [branch]</code> - Switch branch
<code>git merge [branch]</code> - Merge branch

<b>Undo Changes:</b>
<code>git reset HEAD~1</code> - Undo last commit
<code>git revert [commit]</code> - Revert commit
<code>git stash</code> - Stash changes

<b>Remote:</b>
<code>git remote -v</code> - List remotes
<code>git remote add origin [url]</code> - Add remote
"""
    
    await callback.message.edit_text(text, reply_markup=get_back_to_menu_button())
    await callback.answer()
