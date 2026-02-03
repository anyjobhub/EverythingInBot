"""
M5: Tools & Utilities Handler
PDF, Image, Text, URL, QR, Converters, Calculators
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Document
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.bot.keyboards.main_menu import get_back_to_menu_button
from worker.tasks import merge_pdfs, compress_pdf, ocr_pdf

router = Router(name="m5_tools")


class ToolsStates(StatesGroup):
    """FSM States for Tools"""
    waiting_for_pdf = State()
    waiting_for_image = State()
    waiting_for_text = State()
    waiting_for_url = State()


@router.callback_query(F.data == "module_tools")
async def show_tools_menu(callback: CallbackQuery):
    """Show Tools & Utilities menu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📄 PDF Tools", callback_data="tools_pdf"),
        InlineKeyboardButton(text="🖼 Image Tools", callback_data="tools_image")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Text Tools", callback_data="tools_text"),
        InlineKeyboardButton(text="🔗 URL Tools", callback_data="tools_url")
    )
    builder.row(
        InlineKeyboardButton(text="📱 QR/Barcode", callback_data="tools_qr"),
        InlineKeyboardButton(text="🔄 Converters", callback_data="tools_convert")
    )
    builder.row(
        InlineKeyboardButton(text="🧮 Calculators", callback_data="tools_calc")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    )
    
    text = """
🛠 <b>Tools & Utilities</b>

Your Swiss-Army Knife of productivity tools!

<b>Available Tools:</b>

📄 <b>PDF Suite</b> - Merge, Split, Compress, OCR
🖼 <b>Image Tools</b> - Remove BG, Resize, Convert
📝 <b>Text Tools</b> - Summarize, Rephrase, Format
🔗 <b>URL Tools</b> - Shorten, Expand, Safety Check
📱 <b>QR/Barcode</b> - Generate & Scan
🔄 <b>Converters</b> - PDF↔Word, Image↔Text, Audio↔Text
🧮 <b>Calculators</b> - GST, EMI, Salary, Currency

Choose a category to get started!
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "tools_pdf")
async def show_pdf_tools(callback: CallbackQuery):
    """Show PDF tools"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📑 Merge PDFs", callback_data="pdf_merge"),
        InlineKeyboardButton(text="✂️ Split PDF", callback_data="pdf_split")
    )
    builder.row(
        InlineKeyboardButton(text="🗜 Compress PDF", callback_data="pdf_compress"),
        InlineKeyboardButton(text="👁 Extract Text (OCR)", callback_data="pdf_ocr")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_tools")
    )
    
    await callback.message.edit_text(
        "📄 <b>PDF Tools</b>\n\nSelect a PDF operation:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "pdf_compress")
async def start_pdf_compress(callback: CallbackQuery, state: FSMContext):
    """Start PDF compression"""
    await callback.message.edit_text(
        "🗜 <b>Compress PDF</b>\n\nSend me a PDF file to compress:",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(ToolsStates.waiting_for_pdf)
    await state.update_data(operation="compress")
    await callback.answer()


@router.message(ToolsStates.waiting_for_pdf, F.document)
async def process_pdf(message: Message, state: FSMContext):
    """Process PDF file"""
    document: Document = message.document
    
    # Check if it's a PDF
    if not document.file_name.endswith('.pdf'):
        await message.answer("❌ Please send a PDF file.")
        return
    
    data = await state.get_data()
    operation = data.get("operation", "compress")
    
    processing_msg = await message.answer(f"⚙️ Processing PDF...")
    
    # Download file
    file = await message.bot.get_file(document.file_id)
    file_path = f"/tmp/{document.file_name}"
    await message.bot.download_file(file.file_path, file_path)
    
    # Call Celery task
    if operation == "compress":
        result = compress_pdf.delay(file_path)
    
    # Placeholder response
    response = f"""
✅ <b>PDF Processed!</b>

<b>Original:</b> {document.file_name}
<b>Size:</b> {document.file_size / 1024:.2f} KB
<b>Operation:</b> {operation.title()}

<i>Note: File processing will be implemented with Celery tasks</i>
"""
    
    await processing_msg.edit_text(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "tools_calc")
async def show_calculators(callback: CallbackQuery):
    """Show calculators"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💰 GST Calculator", callback_data="calc_gst"),
        InlineKeyboardButton(text="🏦 EMI Calculator", callback_data="calc_emi")
    )
    builder.row(
        InlineKeyboardButton(text="💵 Salary Calculator", callback_data="calc_salary"),
        InlineKeyboardButton(text="💱 Currency Converter", callback_data="calc_currency")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Percentage", callback_data="calc_percent")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_tools")
    )
    
    await callback.message.edit_text(
        "🧮 <b>Calculators</b>\n\nSelect a calculator:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "calc_gst")
async def gst_calculator(callback: CallbackQuery):
    """GST Calculator"""
    response = """
💰 <b>GST Calculator</b>

Send amount in format:
<code>1000 18</code>

Where:
• 1000 = Base amount
• 18 = GST percentage

Example calculations:
• Base: ₹1000, GST 18%
• GST Amount: ₹180
• Total: ₹1180

<i>Send your amount and GST % to calculate</i>
"""
    
    await callback.message.edit_text(response, reply_markup=get_back_to_menu_button())
    await callback.answer()
