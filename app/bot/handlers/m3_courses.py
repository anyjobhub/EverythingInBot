"""
M3: Courses & Learning Handler (FULLY AUTOMATED)
Live course fetching from 6 platforms with category filtering
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.database import Database
from app.utils.logger import log_button_click, log_search, log_action

router = Router(name="m3_courses")


class CourseStates(StatesGroup):
    """FSM States for Courses module"""
    searching = State()


# Pagination state storage
user_course_pages = {}


@router.callback_query(F.data == "module_courses")
async def show_courses_menu(callback: CallbackQuery):
    """Show Courses & Learning main menu"""
    # Log module access
    db = Database.get_db()
    await log_button_click(db, callback.from_user.id, "module_courses", "m3_courses")
    
    builder = InlineKeyboardBuilder()
    
    # Category buttons
    builder.row(
        InlineKeyboardButton(text="🐍 Python", callback_data="courses_python"),
        InlineKeyboardButton(text="🔒 Cybersecurity", callback_data="courses_cybersecurity")
    )
    builder.row(
        InlineKeyboardButton(text="🤖 AI & ML", callback_data="courses_ai"),
        InlineKeyboardButton(text="🌐 Web Dev", callback_data="courses_web")
    )
    builder.row(
        InlineKeyboardButton(text="☁️ Cloud & DevOps", callback_data="courses_cloud"),
        InlineKeyboardButton(text="📊 Data Science", callback_data="courses_data")
    )
    builder.row(
        InlineKeyboardButton(text="📱 Mobile Dev", callback_data="courses_mobile"),
        InlineKeyboardButton(text="🎯 All Courses", callback_data="courses_all")
    )
    builder.row(
        InlineKeyboardButton(text="🔍 Search Courses", callback_data="courses_search")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    )
    
    text = """
📚 <b>Courses & Learning</b>

🌟 <b>Free Courses from Top Platforms</b>

<b>Platforms:</b>
• ClassCentral
• Coursera
• edX
• freeCodeCamp
• YouTube

🔄 <b>Auto-updated every 12 hours</b>
📖 <b>500+ free courses</b>

<b>Categories:</b>
🐍 Python Programming
🔒 Cybersecurity & Ethical Hacking
🤖 AI & Machine Learning
🌐 Web Development
☁️ Cloud & DevOps
📊 Data Science
📱 Mobile Development

Choose a category to explore courses:
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "courses_python")
async def show_python_courses(callback: CallbackQuery):
    """Show Python courses"""
    await show_category_courses(callback, "python", "Python Programming")


@router.callback_query(F.data == "courses_cybersecurity")
async def show_cybersecurity_courses(callback: CallbackQuery):
    """Show Cybersecurity courses"""
    await show_category_courses(callback, "cybersecurity", "Cybersecurity")


@router.callback_query(F.data == "courses_ai")
async def show_ai_courses(callback: CallbackQuery):
    """Show AI & ML courses"""
    await show_category_courses(callback, "ai", "AI & Machine Learning")


@router.callback_query(F.data == "courses_web")
async def show_web_courses(callback: CallbackQuery):
    """Show Web Development courses"""
    await show_category_courses(callback, "web_development", "Web Development")


@router.callback_query(F.data == "courses_cloud")
async def show_cloud_courses(callback: CallbackQuery):
    """Show Cloud & DevOps courses"""
    await show_category_courses(callback, "cloud", "Cloud & DevOps")


@router.callback_query(F.data == "courses_data")
async def show_data_courses(callback: CallbackQuery):
    """Show Data Science courses"""
    await show_category_courses(callback, "data_science", "Data Science")


@router.callback_query(F.data == "courses_mobile")
async def show_mobile_courses(callback: CallbackQuery):
    """Show Mobile Development courses"""
    await show_category_courses(callback, "mobile", "Mobile Development")


@router.callback_query(F.data == "courses_all")
async def show_all_courses(callback: CallbackQuery):
    """Show all courses"""
    user_id = callback.from_user.id
    db = Database.get_db()
    
    await log_button_click(db, user_id, "courses_all", "m3_courses")
    
    courses = await db.courses.find().sort("fetched_at", -1).limit(10).to_list(length=10)
    
    if not courses:
        await callback.answer("No courses available yet. Please wait for data fetch.", show_alert=True)
        return
    
    user_course_pages[user_id] = {
        'filter': {},
        'page': 0,
        'category': 'all'
    }
    
    await display_courses_page(callback.message, courses, user_id, 0, "All Courses")
    await callback.answer()


async def show_category_courses(callback: CallbackQuery, category: str, title: str):
    """Show courses for a specific category"""
    user_id = callback.from_user.id
    db = Database.get_db()
    
    await log_button_click(db, user_id, f"courses_{category}", "m3_courses")
    
    courses = await db.courses.find(
        {"category": category}
    ).sort("fetched_at", -1).limit(10).to_list(length=10)
    
    if not courses:
        await callback.answer(f"No {title} courses available yet.", show_alert=True)
        return
    
    user_course_pages[user_id] = {
        'filter': {'category': category},
        'page': 0,
        'category': category
    }
    
    await display_courses_page(callback.message, courses, user_id, 0, title)
    await callback.answer()


@router.callback_query(F.data == "courses_search")
async def start_course_search(callback: CallbackQuery, state: FSMContext):
    """Start course search"""
    db = Database.get_db()
    await log_button_click(db, callback.from_user.id, "courses_search", "m3_courses")
    
    await callback.message.edit_text(
        "🔍 <b>Search Courses</b>\n\nEnter keywords to search for courses:\n\n<i>Example: python, machine learning, react</i>",
        reply_markup=InlineKeyboardBuilder().row(
            InlineKeyboardButton(text="🔙 Back", callback_data="module_courses")
        ).as_markup()
    )
    await state.set_state(CourseStates.searching)
    await callback.answer()


@router.message(CourseStates.searching)
async def process_course_search(message: Message, state: FSMContext):
    """Process course search query"""
    query = message.text.strip()
    user_id = message.from_user.id
    db = Database.get_db()
    
    # Log search
    await log_search(db, user_id, query, "m3_courses", {"action": "course_search"})
    
    # Search in title, description, instructor
    courses = await db.courses.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"instructor": {"$regex": query, "$options": "i"}},
            {"platform": {"$regex": query, "$options": "i"}}
        ]
    }).sort("fetched_at", -1).limit(10).to_list(length=10)
    
    if not courses:
        await message.answer(
            f"❌ No courses found for '<b>{query}</b>'\n\nTry different keywords.",
            reply_markup=InlineKeyboardBuilder().row(
                InlineKeyboardButton(text="🔙 Back to Courses", callback_data="module_courses")
            ).as_markup()
        )
        await state.clear()
        return
    
    user_course_pages[user_id] = {
        'filter': {'query': query},
        'page': 0,
        'category': 'search'
    }
    
    await display_courses_page(message, courses, user_id, 0, f"Search: {query}")
    await state.clear()


@router.callback_query(F.data.startswith("course_page_"))
async def handle_course_pagination(callback: CallbackQuery):
    """Handle course pagination (next/prev)"""
    user_id = callback.from_user.id
    page = int(callback.data.split("_")[-1])
    
    if user_id not in user_course_pages:
        await callback.answer("Session expired. Please search again.", show_alert=True)
        return
    
    db = Database.get_db()
    filter_query = user_course_pages[user_id]['filter']
    
    # Fetch courses for this page
    skip = page * 10
    courses = await db.courses.find(filter_query).sort("fetched_at", -1).skip(skip).limit(10).to_list(length=10)
    
    if not courses:
        await callback.answer("No more courses available.", show_alert=True)
        return
    
    user_course_pages[user_id]['page'] = page
    category = user_course_pages[user_id].get('category', 'Courses')
    
    await display_courses_page(callback.message, courses, user_id, page, category.title())
    await callback.answer()


async def display_courses_page(message, courses: list, user_id: int, page: int, title: str):
    """Display a page of courses with pagination"""
    if not courses:
        return
    
    # Display first 3 courses in detail
    text = f"📚 <b>{title}</b>\n\n"
    text += f"📄 Page {page + 1} | Showing {len(courses)} courses\n\n"
    
    for i, course in enumerate(courses[:3], 1):
        text += f"<b>{i}. {course.get('title', 'Untitled')}</b>\n"
        text += f"🎓 Platform: {course.get('platform', 'Unknown').title()}\n"
        
        if course.get('instructor'):
            text += f"👨‍🏫 Instructor: {course['instructor']}\n"
        
        if course.get('difficulty'):
            text += f"⭐ Level: {course['difficulty'].title()}\n"
        
        if course.get('duration'):
            text += f"⏱ Duration: {course['duration']}\n"
        
        text += f"🔗 <a href='{course.get('url', '#')}'>Start Course</a>\n\n"
    
    # Pagination buttons
    builder = InlineKeyboardBuilder()
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"course_page_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text="🔄 Refresh", callback_data="module_courses"))
    nav_buttons.append(InlineKeyboardButton(text="➡️ Next", callback_data=f"course_page_{page+1}"))
    
    builder.row(*nav_buttons)
    builder.row(InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu"))
    
    try:
        await message.edit_text(text, reply_markup=builder.as_markup(), disable_web_page_preview=True)
    except:
        await message.answer(text, reply_markup=builder.as_markup(), disable_web_page_preview=True)
