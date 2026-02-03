"""
M4: Jobs & Careers Handler (FULLY AUTOMATED)
Live job fetching from 12 sources with advanced filtering
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.database import Database
from app.utils.logger import log_button_click, log_search, log_action
from datetime import datetime

router = Router(name="m4_jobs")


class JobStates(StatesGroup):
    """FSM States for Jobs module"""
    searching = State()
    filtering = State()


# Pagination state storage (in production, use Redis)
user_job_pages = {}


@router.callback_query(F.data == "module_jobs")
async def show_jobs_menu(callback: CallbackQuery):
    """Show Jobs & Careers main menu"""
    # Log module access
    db = Database.get_db()
    await log_button_click(db, callback.from_user.id, "module_jobs", "m4_jobs")
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 Latest Jobs", callback_data="jobs_latest"),
        InlineKeyboardButton(text="🔥 Trending Jobs", callback_data="jobs_trending")
    )
    builder.row(
        InlineKeyboardButton(text="🏛 Government Jobs (India)", callback_data="jobs_government"),
        InlineKeyboardButton(text="🌍 Remote Jobs", callback_data="jobs_remote")
    )
    builder.row(
        InlineKeyboardButton(text="💻 IT/Software Jobs", callback_data="jobs_it"),
        InlineKeyboardButton(text="🎓 Internships", callback_data="jobs_internship")
    )
    builder.row(
        InlineKeyboardButton(text="🔍 Search Jobs", callback_data="jobs_search"),
        InlineKeyboardButton(text="⚙️ Filter Jobs", callback_data="jobs_filter")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    )
    
    text = """
💼 <b>Jobs & Careers</b>

🌟 <b>Live Job Listings from 12+ Sources</b>

<b>Global Sources:</b>
• Remotive (Remote Jobs)
• Arbeitnow (Global Jobs)
• US Government Jobs
• Indeed

<b>India Sources:</b>
• Sarkari Exam
• Hindustan Times
• The Hindu
• FreeJobAlert
• AICTE Internships
• And more...

🔄 <b>Auto-updated every 6 hours</b>
📊 <b>1000+ active listings</b>

Choose a category to browse jobs:
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "jobs_latest")
async def show_latest_jobs(callback: CallbackQuery):
    """Show latest jobs from all sources"""
    user_id = callback.from_user.id
    db = Database.get_db()
    
    # Log button click
    await log_button_click(db, user_id, "jobs_latest", "m4_jobs")
    
    # Fetch latest jobs
    jobs = await db.jobs.find().sort("fetched_at", -1).limit(10).to_list(length=10)
    
    if not jobs:
        await callback.answer("No jobs available yet. Please wait for data fetch.", show_alert=True)
        return
    
    # Store pagination state
    user_job_pages[user_id] = {
        'filter': {},
        'page': 0,
        'category': 'latest'
    }
    
    await display_jobs_page(callback.message, jobs, user_id, 0, "Latest Jobs")
    await callback.answer()


@router.callback_query(F.data == "jobs_trending")
async def show_trending_jobs(callback: CallbackQuery):
    """Show trending jobs (most recent + IT category)"""
    user_id = callback.from_user.id
    db = Database.get_db()
    
    await log_button_click(db, user_id, "jobs_trending", "m4_jobs")
    
    # Trending = recent IT jobs
    jobs = await db.jobs.find(
        {"category": "IT"}
    ).sort("fetched_at", -1).limit(10).to_list(length=10)
    
    if not jobs:
        await callback.answer("No trending jobs available.", show_alert=True)
        return
    
    user_job_pages[user_id] = {
        'filter': {'category': 'IT'},
        'page': 0,
        'category': 'trending'
    }
    
    await display_jobs_page(callback.message, jobs, user_id, 0, "Trending IT Jobs")
    await callback.answer()


@router.callback_query(F.data == "jobs_government")
async def show_government_jobs(callback: CallbackQuery):
    """Show government jobs (India)"""
    user_id = callback.from_user.id
    db = Database.get_db()
    
    await log_button_click(db, user_id, "jobs_government", "m4_jobs")
    
    jobs = await db.jobs.find(
        {"category": "government", "country": "india"}
    ).sort("fetched_at", -1).limit(10).to_list(length=10)
    
    if not jobs:
        await callback.answer("No government jobs available.", show_alert=True)
        return
    
    user_job_pages[user_id] = {
        'filter': {'category': 'government', 'country': 'india'},
        'page': 0,
        'category': 'government'
    }
    
    await display_jobs_page(callback.message, jobs, user_id, 0, "Government Jobs (India)")
    await callback.answer()


@router.callback_query(F.data == "jobs_remote")
async def show_remote_jobs(callback: CallbackQuery):
    """Show remote jobs"""
    user_id = callback.from_user.id
    db = Database.get_db()
    
    await log_button_click(db, user_id, "jobs_remote", "m4_jobs")
    
    jobs = await db.jobs.find(
        {"type": "remote"}
    ).sort("fetched_at", -1).limit(10).to_list(length=10)
    
    if not jobs:
        await callback.answer("No remote jobs available.", show_alert=True)
        return
    
    user_job_pages[user_id] = {
        'filter': {'type': 'remote'},
        'page': 0,
        'category': 'remote'
    }
    
    await display_jobs_page(callback.message, jobs, user_id, 0, "Remote Jobs")
    await callback.answer()


@router.callback_query(F.data == "jobs_it")
async def show_it_jobs(callback: CallbackQuery):
    """Show IT/Software jobs"""
    user_id = callback.from_user.id
    db = Database.get_db()
    
    await log_button_click(db, user_id, "jobs_it", "m4_jobs")
    
    jobs = await db.jobs.find(
        {"category": "IT"}
    ).sort("fetched_at", -1).limit(10).to_list(length=10)
    
    if not jobs:
        await callback.answer("No IT jobs available.", show_alert=True)
        return
    
    user_job_pages[user_id] = {
        'filter': {'category': 'IT'},
        'page': 0,
        'category': 'it'
    }
    
    await display_jobs_page(callback.message, jobs, user_id, 0, "IT/Software Jobs")
    await callback.answer()


@router.callback_query(F.data == "jobs_internship")
async def show_internship_jobs(callback: CallbackQuery):
    """Show internship opportunities"""
    user_id = callback.from_user.id
    db = Database.get_db()
    
    await log_button_click(db, user_id, "jobs_internship", "m4_jobs")
    
    jobs = await db.jobs.find(
        {"category": "internship"}
    ).sort("fetched_at", -1).limit(10).to_list(length=10)
    
    if not jobs:
        await callback.answer("No internships available.", show_alert=True)
        return
    
    user_job_pages[user_id] = {
        'filter': {'category': 'internship'},
        'page': 0,
        'category': 'internship'
    }
    
    await display_jobs_page(callback.message, jobs, user_id, 0, "Internships")
    await callback.answer()


@router.callback_query(F.data == "jobs_search")
async def start_job_search(callback: CallbackQuery, state: FSMContext):
    """Start job search"""
    db = Database.get_db()
    await log_button_click(db, callback.from_user.id, "jobs_search", "m4_jobs")
    
    await callback.message.edit_text(
        "🔍 <b>Search Jobs</b>\n\nEnter keywords to search for jobs:\n\n<i>Example: python developer, data scientist, remote</i>",
        reply_markup=InlineKeyboardBuilder().row(
            InlineKeyboardButton(text="🔙 Back", callback_data="module_jobs")
        ).as_markup()
    )
    await state.set_state(JobStates.searching)
    await callback.answer()


@router.message(JobStates.searching)
async def process_job_search(message: Message, state: FSMContext):
    """Process job search query"""
    query = message.text.strip()
    user_id = message.from_user.id
    db = Database.get_db()
    
    # Log search
    await log_search(db, user_id, query, "m4_jobs", {"action": "job_search"})
    
    # Search in title, company, description, tags
    jobs = await db.jobs.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"company": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"tags": {"$regex": query, "$options": "i"}}
        ]
    }).sort("fetched_at", -1).limit(10).to_list(length=10)
    
    if not jobs:
        await message.answer(
            f"❌ No jobs found for '<b>{query}</b>'\n\nTry different keywords.",
            reply_markup=InlineKeyboardBuilder().row(
                InlineKeyboardButton(text="🔙 Back to Jobs", callback_data="module_jobs")
            ).as_markup()
        )
        await state.clear()
        return
    
    user_job_pages[user_id] = {
        'filter': {'query': query},
        'page': 0,
        'category': 'search'
    }
    
    await display_jobs_page(message, jobs, user_id, 0, f"Search: {query}")
    await state.clear()


@router.callback_query(F.data.startswith("job_page_"))
async def handle_job_pagination(callback: CallbackQuery):
    """Handle job pagination (next/prev)"""
    user_id = callback.from_user.id
    page = int(callback.data.split("_")[-1])
    
    if user_id not in user_job_pages:
        await callback.answer("Session expired. Please search again.", show_alert=True)
        return
    
    db = Database.get_db()
    filter_query = user_job_pages[user_id]['filter']
    
    # Fetch jobs for this page
    skip = page * 10
    jobs = await db.jobs.find(filter_query).sort("fetched_at", -1).skip(skip).limit(10).to_list(length=10)
    
    if not jobs:
        await callback.answer("No more jobs available.", show_alert=True)
        return
    
    user_job_pages[user_id]['page'] = page
    category = user_job_pages[user_id].get('category', 'Jobs')
    
    await display_jobs_page(callback.message, jobs, user_id, page, category.title())
    await callback.answer()


async def display_jobs_page(message, jobs: list, user_id: int, page: int, title: str):
    """Display a page of jobs with pagination"""
    if not jobs:
        return
    
    # Display first 3 jobs in detail
    text = f"💼 <b>{title}</b>\n\n"
    text += f"📄 Page {page + 1} | Showing {len(jobs)} jobs\n\n"
    
    for i, job in enumerate(jobs[:3], 1):
        text += f"<b>{i}. {job.get('title', 'Untitled')}</b>\n"
        text += f"🏢 {job.get('company', 'Unknown')}\n"
        text += f"📍 {job.get('location', 'Not specified')}\n"
        
        if job.get('salary'):
            text += f"💰 {job['salary']}\n"
        
        if job.get('type'):
            text += f"🏷 {job['type'].title()}\n"
        
        text += f"🔗 <a href='{job.get('url', '#')}'>Apply Now</a>\n\n"
    
    # Pagination buttons
    builder = InlineKeyboardBuilder()
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"job_page_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text="🔄 Refresh", callback_data="module_jobs"))
    nav_buttons.append(InlineKeyboardButton(text="➡️ Next", callback_data=f"job_page_{page+1}"))
    
    builder.row(*nav_buttons)
    builder.row(InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu"))
    
    try:
        await message.edit_text(text, reply_markup=builder.as_markup(), disable_web_page_preview=True)
    except:
        await message.answer(text, reply_markup=builder.as_markup(), disable_web_page_preview=True)
