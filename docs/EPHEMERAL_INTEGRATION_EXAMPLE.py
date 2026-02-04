"""
Example: Adding Ephemeral Mode to Job Search Handler
This shows how to integrate ephemeral auto-delete to any search handler
"""

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.config import settings
from app.services.search_logger import search_logger
from app.services.ephemeral_cleanup import ephemeral_cleanup
from app.database import Database

router = Router(name="example_ephemeral")

# Admin IDs (from config)
ADMIN_IDS = getattr(settings, 'ADMIN_IDS', [])


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS


# EXAMPLE 1: Job Search with Ephemeral Mode
async def process_job_search_with_ephemeral(message: Message, state: FSMContext, **data):
    """
    Process job search query with ephemeral auto-delete
    
    IMPORTANT: Use sanitized text from middleware
    """
    # ✅ Get sanitized text from middleware data dict
    query = data.get("sanitized_text") or message.text
    query = query.strip()
    
    user_id = message.from_user.id
    username = message.from_user.username
    db = Database.get_db()
    
    # Check if user is admin
    user_is_admin = is_admin(user_id)
    
    # Search jobs in database
    jobs = await db.jobs.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"company": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}}
        ]
    }).sort("fetched_at", -1).limit(10).to_list(length=10)
    
    if not jobs:
        # No results - don't log or schedule deletion
        await message.answer(
            f"❌ No jobs found for '<b>{query}</b>'\n\nTry different keywords."
        )
        await state.clear()
        return
    
    # Build results message
    text = f"💼 <b>Job Search Results: {query}</b>\n\n"
    text += f"Found {len(jobs)} jobs:\n\n"
    
    for i, job in enumerate(jobs[:5], 1):
        text += f"<b>{i}. {job.get('title', 'Untitled')}</b>\n"
        text += f"🏢 {job.get('company', 'Unknown')}\n"
        text += f"📍 {job.get('location', 'Not specified')}\n"
        text += f"🔗 <a href='{job.get('url', '#')}'>Apply Now</a>\n\n"
    
    # Add ephemeral notice (only for non-admins)
    if not user_is_admin:
        text += "\n<i>⏱ This message will auto-delete in 5 minutes</i>"
    
    # Send results
    result_msg = await message.answer(text, disable_web_page_preview=True)
    
    # Log search to MongoDB
    await search_logger.log_search(
        user_id=user_id,
        query=query,
        result_message_id=result_msg.message_id,
        chat_id=message.chat.id,
        module_name="m4_jobs",
        username=username,
        is_admin=user_is_admin,
        expiry_seconds=300,  # 5 minutes
        results_count=len(jobs)
    )
    
    # Schedule auto-deletion (non-blocking)
    # Admin messages are NOT deleted
    ephemeral_cleanup.create_deletion_task(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=result_msg.message_id,
        delay_seconds=300,  # 5 minutes
        is_admin=user_is_admin
    )
    
    await state.clear()


# EXAMPLE 2: Course Search with Ephemeral Mode
async def process_course_search_with_ephemeral(message: Message, state: FSMContext, **data):
    """
    Process course search query with ephemeral auto-delete
    """
    # ✅ Get sanitized text
    query = data.get("sanitized_text") or message.text
    query = query.strip()
    
    user_id = message.from_user.id
    username = message.from_user.username
    user_is_admin = is_admin(user_id)
    db = Database.get_db()
    
    # Search courses
    courses = await db.courses.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"platform": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}}
        ]
    }).sort("fetched_at", -1).limit(10).to_list(length=10)
    
    if not courses:
        await message.answer(
            f"❌ No courses found for '<b>{query}</b>'\n\nTry different keywords."
        )
        await state.clear()
        return
    
    # Build results
    text = f"📚 <b>Course Search Results: {query}</b>\n\n"
    
    for i, course in enumerate(courses[:5], 1):
        text += f"<b>{i}. {course.get('title', 'Untitled')}</b>\n"
        text += f"🎓 {course.get('platform', 'Unknown')}\n"
        text += f"🔗 <a href='{course.get('url', '#')}'>Enroll Now</a>\n\n"
    
    if not user_is_admin:
        text += "\n<i>⏱ This message will auto-delete in 5 minutes</i>"
    
    # Send results
    result_msg = await message.answer(text, disable_web_page_preview=True)
    
    # Log search
    await search_logger.log_search(
        user_id=user_id,
        query=query,
        result_message_id=result_msg.message_id,
        chat_id=message.chat.id,
        module_name="m3_courses",
        username=username,
        is_admin=user_is_admin,
        results_count=len(courses)
    )
    
    # Schedule deletion (non-blocking)
    ephemeral_cleanup.create_deletion_task(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=result_msg.message_id,
        delay_seconds=300,
        is_admin=user_is_admin
    )
    
    await state.clear()


# EXAMPLE 3: Handling Expired Message Interactions
async def handle_expired_callback(callback_query):
    """
    Handle callback queries on expired/deleted messages
    """
    from aiogram.exceptions import TelegramBadRequest
    
    try:
        # Try to answer the callback
        await callback_query.answer(
            "⚠️ This search result has expired. Please search again.",
            show_alert=True
        )
    except TelegramBadRequest:
        # Message already deleted
        pass


# INTEGRATION CHECKLIST:
# 
# 1. ✅ Import services:
#    from app.services.search_logger import search_logger
#    from app.services.ephemeral_cleanup import ephemeral_cleanup
#
# 2. ✅ Check if user is admin:
#    user_is_admin = is_admin(message.from_user.id)
#
# 3. ✅ Use sanitized text from middleware:
#    query = data.get("sanitized_text") or message.text
#
# 4. ✅ Send results and capture message:
#    result_msg = await message.answer(...)
#
# 5. ✅ Log search:
#    await search_logger.log_search(...)
#
# 6. ✅ Schedule deletion (non-blocking):
#    ephemeral_cleanup.create_deletion_task(...)
#
# 7. ✅ Add ephemeral notice to message (non-admins only)
#
# 8. ✅ Handle expired message callbacks gracefully
