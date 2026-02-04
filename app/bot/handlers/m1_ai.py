"""
M1: AI Engine Hub Handler
Multi-AI integration (GPT-4o, Claude, Gemini, Ollama)
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.bot.keyboards.main_menu import get_back_to_menu_button
from app.tasks.ai_tasks import generate_ai_response, generate_image
from app.database import Database
from app.utils.logger import log_button_click, log_search, log_action

router = Router(name="m1_ai")


class AIStates(StatesGroup):
    """FSM States for AI module"""
    waiting_for_prompt = State()
    waiting_for_image_prompt = State()
    selecting_model = State()


@router.callback_query(F.data == "module_ai")
async def show_ai_menu(callback: CallbackQuery):
    """Show AI Engine menu"""
    # Log module access
    db = Database.get_db()
    await log_button_click(db, callback.from_user.id, "module_ai", "m1_ai")
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💬 Chat with AI", callback_data="ai_chat"),
        InlineKeyboardButton(text="🎨 Generate Image", callback_data="ai_image")
    )
    builder.row(
        InlineKeyboardButton(text="👁 Vision (Image Analysis)", callback_data="ai_vision"),
        InlineKeyboardButton(text="📄 Analyze Document", callback_data="ai_document")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Select AI Model", callback_data="ai_select_model")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    )
    
    text = """
🤖 <b>AI Engine Hub</b>

Choose an AI feature:

💬 <b>Chat with AI</b> - Talk with GPT-4o, Claude, or Gemini
🎨 <b>Generate Image</b> - Create images with DALL-E
👁 <b>Vision</b> - Analyze images with AI
📄 <b>Analyze Document</b> - PDF summary, resume optimization

<b>Available Models:</b>
• GPT-4o (OpenAI)
• Claude 3.5 Sonnet (Anthropic)
• Gemini 1.5 Pro (Google)
• Llama 3 (Local)
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "ai_chat")
async def start_ai_chat(callback: CallbackQuery, state: FSMContext):
    """Start AI chat"""
    # Log button click
    db = Database.get_db()
    await log_button_click(db, callback.from_user.id, "ai_chat", "m1_ai")
    
    await callback.message.edit_text(
        "💬 <b>AI Chat</b>\n\nSend me your question or prompt:",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(AIStates.waiting_for_prompt)
    await callback.answer()


@router.message(AIStates.waiting_for_prompt)
async def process_ai_prompt(message: Message, state: FSMContext):
    """Process AI prompt"""
    prompt = message.text
    
    # Log AI search
    db = Database.get_db()
    await log_search(db, message.from_user.id, prompt, "m1_ai", {"action": "ai_chat", "model": "gpt-4o"})
    
    # Send "thinking" message
    thinking_msg = await message.answer("🤔 Thinking...")
    
    # Call Celery task (async)
    # In production, you'd wait for the result
    # For now, placeholder response
    result = generate_ai_response.delay(prompt, model="gpt-4o")
    
    # Placeholder response
    response = f"""
🤖 <b>AI Response:</b>

This is a placeholder response. In production, this will use:
- GPT-4o for advanced reasoning
- Claude 3.5 for long-form content
- Gemini 1.5 for multimodal tasks

Your prompt: <i>{prompt}</i>

<i>Note: Connect API keys to enable AI responses</i>
"""
    
    await thinking_msg.edit_text(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "ai_image")
async def start_image_generation(callback: CallbackQuery, state: FSMContext):
    """Start image generation"""
    # Log button click
    db = Database.get_db()
    await log_button_click(db, callback.from_user.id, "ai_image", "m1_ai")
    
    await callback.message.edit_text(
        "🎨 <b>AI Image Generation</b>\n\nDescribe the image you want to create:",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(AIStates.waiting_for_image_prompt)
    await callback.answer()


@router.message(AIStates.waiting_for_image_prompt)
async def process_image_prompt(message: Message, state: FSMContext):
    """Process image generation prompt"""
    prompt = message.text
    
    # Log image generation
    db = Database.get_db()
    await log_search(db, message.from_user.id, prompt, "m1_ai", {"action": "image_generation", "model": "dall-e-3"})
    
    generating_msg = await message.answer("🎨 Generating image...")
    
    # Call Celery task
    result = generate_image.delay(prompt, model="dall-e-3")
    
    # Placeholder
    response = f"""
🎨 <b>Image Generated!</b>

Prompt: <i>{prompt}</i>

<i>Note: Connect DALL-E API key to generate actual images</i>
"""
    
    await generating_msg.edit_text(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "ai_select_model")
async def select_ai_model(callback: CallbackQuery):
    """Select AI model"""
    # Log button click
    db = Database.get_db()
    await log_button_click(db, callback.from_user.id, "ai_select_model", "m1_ai")
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🟢 GPT-4o", callback_data="model_gpt4o"),
        InlineKeyboardButton(text="🔵 Claude 3.5", callback_data="model_claude")
    )
    builder.row(
        InlineKeyboardButton(text="🟡 Gemini 1.5", callback_data="model_gemini"),
        InlineKeyboardButton(text="⚪ Llama 3", callback_data="model_llama")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_ai")
    )
    
    await callback.message.edit_text(
        "⚙️ <b>Select AI Model</b>\n\nChoose your preferred AI model:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()
