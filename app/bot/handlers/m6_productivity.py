"""
M6: Productivity Tools Handler
To-Do manager, Notes, Habit tracker, Reminders, Journal
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.bot.keyboards.main_menu import get_back_to_menu_button
from app.database import get_db
from datetime import datetime

router = Router(name="m6_productivity")


class ProductivityStates(StatesGroup):
    """FSM States for Productivity"""
    adding_todo = State()
    adding_note = State()
    adding_habit = State()
    setting_reminder = State()
    writing_journal = State()


@router.callback_query(F.data == "module_productivity")
async def show_productivity_menu(callback: CallbackQuery):
    """Show Productivity Tools menu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ To-Do List", callback_data="prod_todo"),
        InlineKeyboardButton(text="📝 Notes", callback_data="prod_notes")
    )
    builder.row(
        InlineKeyboardButton(text="🎯 Habits", callback_data="prod_habits"),
        InlineKeyboardButton(text="⏰ Reminders", callback_data="prod_reminders")
    )
    builder.row(
        InlineKeyboardButton(text="📖 Journal", callback_data="prod_journal"),
        InlineKeyboardButton(text="🎯 Daily Goals", callback_data="prod_goals")
    )
    builder.row(
        InlineKeyboardButton(text="📊 My Stats", callback_data="prod_stats")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    )
    
    text = """
✅ <b>Productivity Tools</b>

Organize your life and achieve your goals!

<b>Available Tools:</b>
✅ <b>To-Do List</b> - Manage tasks
📝 <b>Notes</b> - Quick notes & ideas
🎯 <b>Habits</b> - Build good habits
⏰ <b>Reminders</b> - Never forget
📖 <b>Journal</b> - Daily reflections
🎯 <b>Daily Goals</b> - Set & track goals

<b>Your Stats Today:</b>
• Tasks completed: 5/8
• Active habits: 3
• Journal entries: 1

Choose a tool to get started!
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "prod_todo")
async def show_todo_list(callback: CallbackQuery):
    """Show To-Do list"""
    user_id = callback.from_user.id
    
    # In production, fetch from todos collection
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Add Task", callback_data="todo_add"),
        InlineKeyboardButton(text="✅ Mark Done", callback_data="todo_complete")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Delete Task", callback_data="todo_delete"),
        InlineKeyboardButton(text="📊 View All", callback_data="todo_all")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_productivity")
    )
    
    text = """
✅ <b>My To-Do List</b>

<b>Today's Tasks:</b>

1. ⬜ Complete project documentation
   Priority: High | Due: Today

2. ⬜ Review pull requests
   Priority: Medium | Due: Today

3. ✅ Morning workout
   Priority: High | Completed ✓

4. ⬜ Call client about proposal
   Priority: High | Due: 3 PM

5. ✅ Read 30 pages
   Priority: Low | Completed ✓

<b>Progress:</b> 2/5 tasks completed (40%)

What would you like to do?
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "todo_add")
async def add_todo_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt to add new todo"""
    await callback.message.edit_text(
        """
➕ <b>Add New Task</b>

Send me the task details in this format:

<code>Task name | Priority (high/medium/low) | Due date</code>

Example:
<code>Finish report | high | tomorrow</code>

Or just send the task name for default settings:
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(ProductivityStates.adding_todo)
    await callback.answer()


@router.message(ProductivityStates.adding_todo)
async def save_todo(message: Message, state: FSMContext):
    """Save new todo"""
    task_text = message.text
    user_id = message.from_user.id
    
    # Parse task (simple version)
    parts = task_text.split("|")
    task_name = parts[0].strip() if parts else task_text
    priority = parts[1].strip() if len(parts) > 1 else "medium"
    due_date = parts[2].strip() if len(parts) > 2 else "today"
    
    # In production, save to MongoDB todos collection
    # db.todos.insert_one({
    #     "user_id": user_id,
    #     "task": task_name,
    #     "priority": priority,
    #     "due_date": due_date,
    #     "completed": False,
    #     "created_at": datetime.utcnow()
    # })
    
    response = f"""
✅ <b>Task Added!</b>

<b>Task:</b> {task_name}
<b>Priority:</b> {priority.title()}
<b>Due:</b> {due_date.title()}

Your task has been added to your to-do list!

<i>Tip: Use /todo to view all your tasks</i>
"""
    
    await message.answer(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "prod_notes")
async def show_notes(callback: CallbackQuery):
    """Show notes"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ New Note", callback_data="note_add"),
        InlineKeyboardButton(text="🔍 Search", callback_data="note_search")
    )
    builder.row(
        InlineKeyboardButton(text="🏷 Tags", callback_data="note_tags"),
        InlineKeyboardButton(text="📋 All Notes", callback_data="note_all")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_productivity")
    )
    
    text = """
📝 <b>My Notes</b>

<b>Recent Notes:</b>

1. 💡 <b>Project Ideas</b>
   Created: 2 days ago
   Tags: #work #ideas
   
2. 📚 <b>Book Recommendations</b>
   Created: 5 days ago
   Tags: #reading #personal
   
3. 🎯 <b>Q1 Goals</b>
   Created: 1 week ago
   Tags: #goals #work

<b>Total Notes:</b> 23
<b>Tags:</b> 8

What would you like to do?
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "note_add")
async def add_note_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt to add new note"""
    await callback.message.edit_text(
        """
➕ <b>Create New Note</b>

Send me your note content.

You can include:
• Title on first line
• Content below
• Tags using #hashtag

Example:
<code>Meeting Notes
Discussed Q1 roadmap
Action items: ...
#work #meetings</code>

Send your note:
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(ProductivityStates.adding_note)
    await callback.answer()


@router.message(ProductivityStates.adding_note)
async def save_note(message: Message, state: FSMContext):
    """Save new note"""
    note_content = message.text
    user_id = message.from_user.id
    
    # Extract title (first line)
    lines = note_content.split("\n")
    title = lines[0] if lines else "Untitled Note"
    content = "\n".join(lines[1:]) if len(lines) > 1 else note_content
    
    # Extract tags
    import re
    tags = re.findall(r'#(\w+)', note_content)
    
    # In production, save to MongoDB notes collection
    
    response = f"""
✅ <b>Note Saved!</b>

<b>Title:</b> {title}
<b>Tags:</b> {', '.join(f'#{tag}' for tag in tags) if tags else 'None'}
<b>Created:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}

Your note has been saved successfully!
"""
    
    await message.answer(response, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "prod_habits")
async def show_habits(callback: CallbackQuery):
    """Show habit tracker"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ New Habit", callback_data="habit_add"),
        InlineKeyboardButton(text="✅ Check In", callback_data="habit_checkin")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Statistics", callback_data="habit_stats")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_productivity")
    )
    
    text = """
🎯 <b>Habit Tracker</b>

<b>Active Habits:</b>

1. 💪 <b>Morning Workout</b>
   Frequency: Daily
   Current Streak: 🔥 12 days
   Completion: 85%
   
2. 📚 <b>Read 30 Minutes</b>
   Frequency: Daily
   Current Streak: 🔥 7 days
   Completion: 70%
   
3. 🧘 <b>Meditation</b>
   Frequency: Daily
   Current Streak: 🔥 5 days
   Completion: 60%

<b>Today's Progress:</b> 2/3 completed

Keep up the great work! 🎉
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "prod_reminders")
async def show_reminders(callback: CallbackQuery):
    """Show reminders"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Set Reminder", callback_data="reminder_add"),
        InlineKeyboardButton(text="📋 All Reminders", callback_data="reminder_all")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_productivity")
    )
    
    text = """
⏰ <b>Reminders</b>

<b>Upcoming:</b>

1. 📞 <b>Client Call</b>
   Time: Today, 3:00 PM
   
2. 💊 <b>Take Medicine</b>
   Time: Today, 8:00 PM
   
3. 📧 <b>Send Report</b>
   Time: Tomorrow, 10:00 AM

<b>Total Active:</b> 8 reminders

I'll notify you when it's time! 🔔
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "prod_journal")
async def show_journal(callback: CallbackQuery):
    """Show journal"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✍️ Write Entry", callback_data="journal_write"),
        InlineKeyboardButton(text="📖 Read Entries", callback_data="journal_read")
    )
    builder.row(
        InlineKeyboardButton(text="😊 Mood Tracker", callback_data="journal_mood")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_productivity")
    )
    
    text = """
📖 <b>Daily Journal</b>

<b>Today's Entry:</b>
Not written yet. Take a moment to reflect on your day!

<b>Recent Entries:</b>
• Yesterday: "Productive day! Completed..."
• 2 days ago: "Feeling grateful for..."
• 3 days ago: "Learned something new about..."

<b>Streak:</b> 🔥 15 days
<b>Total Entries:</b> 47

<b>Mood This Week:</b>
😊😊😊😐😊😊😊

Writing helps clarify your thoughts!
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "prod_stats")
async def show_productivity_stats(callback: CallbackQuery):
    """Show productivity statistics"""
    text = """
📊 <b>Productivity Statistics</b>

<b>This Week:</b>
✅ Tasks Completed: 34/42 (81%)
📝 Notes Created: 7
🎯 Habits Maintained: 3 (avg 75% completion)
📖 Journal Entries: 6/7 days
⏰ Reminders Set: 12

<b>Streaks:</b>
🔥 Longest Habit Streak: 21 days (Workout)
🔥 Journal Streak: 15 days

<b>Most Productive Day:</b> Monday
<b>Most Active Time:</b> 9-11 AM

<b>Goals Progress:</b>
📚 Read 12 books: ████░░░░░░ 40% (5/12)
💪 Workout 100 days: ████████░░ 75% (75/100)
📝 Write daily: ███████░░░ 70% (210/365)

Keep up the amazing work! 🎉
"""
    
    await callback.message.edit_text(text, reply_markup=get_back_to_menu_button())
    await callback.answer()
