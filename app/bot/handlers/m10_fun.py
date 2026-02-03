"""
M10: Entertainment & Fun Handler
AI story/joke/poem generators, games, trivia, riddles
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
import random

from app.bot.keyboards.main_menu import get_back_to_menu_button

router = Router(name="m10_fun")


class FunStates(StatesGroup):
    """FSM States for Entertainment"""
    waiting_for_story_prompt = State()
    playing_quiz = State()
    playing_trivia = State()
    playing_riddle = State()


@router.callback_query(F.data == "module_fun")
async def show_fun_menu(callback: CallbackQuery):
    """Show Entertainment menu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📖 AI Story", callback_data="fun_story"),
        InlineKeyboardButton(text="😂 Jokes", callback_data="fun_jokes")
    )
    builder.row(
        InlineKeyboardButton(text="✍️ Poem", callback_data="fun_poem"),
        InlineKeyboardButton(text="🎭 Roast Me", callback_data="fun_roast")
    )
    builder.row(
        InlineKeyboardButton(text="🎮 Quiz Game", callback_data="fun_quiz"),
        InlineKeyboardButton(text="🧠 Trivia", callback_data="fun_trivia")
    )
    builder.row(
        InlineKeyboardButton(text="🎲 Riddles", callback_data="fun_riddle"),
        InlineKeyboardButton(text="💡 Fun Facts", callback_data="fun_facts")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    )
    
    text = """
🎮 <b>Entertainment & Fun</b>

Take a break and have some fun!

<b>AI Generators:</b>
📖 <b>Story Maker</b> - Create unique stories
😂 <b>Jokes</b> - Get funny jokes
✍️ <b>Poem Creator</b> - Generate poems
🎭 <b>Roast Me</b> - Funny roasts

<b>Games:</b>
🎮 <b>Quiz Game</b> - Test your knowledge
🧠 <b>Trivia</b> - Random trivia
🎲 <b>Riddles</b> - Solve riddles
💡 <b>Fun Facts</b> - Learn something new

Choose an option to start having fun!
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "fun_story")
async def story_generator_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for story"""
    await callback.message.edit_text(
        """
📖 <b>AI Story Generator</b>

Tell me what kind of story you want!

Examples:
• "A dragon who loves pizza"
• "A detective solving a mystery in space"
• "A friendship between a robot and a cat"

Send me your story idea:
""",
        reply_markup=get_back_to_menu_button()
    )
    await state.set_state(FunStates.waiting_for_story_prompt)
    await callback.answer()


@router.message(FunStates.waiting_for_story_prompt)
async def generate_story(message: Message, state: FSMContext):
    """Generate AI story"""
    prompt = message.text
    
    # In production, use AI API
    # For now, placeholder story
    
    story = f"""
📖 <b>Your AI-Generated Story</b>

<b>Title:</b> The Adventure of {prompt.split()[0].title() if prompt else 'Mystery'}

Once upon a time, in a land far away, there lived {prompt}. Every day was an adventure, filled with excitement and wonder.

One sunny morning, something extraordinary happened. A mysterious portal appeared, leading to a world beyond imagination. Without hesitation, our hero stepped through...

The journey was filled with challenges, but also incredible discoveries. Along the way, new friends were made, and valuable lessons were learned about courage, friendship, and believing in oneself.

In the end, everything worked out perfectly. The hero returned home, forever changed by the amazing adventure, with stories to tell for generations to come.

<b>The End</b> ✨

<i>Note: Connect AI API for better stories!</i>
"""
    
    await message.answer(story, reply_markup=get_back_to_menu_button())
    await state.clear()


@router.callback_query(F.data == "fun_jokes")
async def tell_joke(callback: CallbackQuery):
    """Tell a random joke"""
    jokes = [
        ("Why do programmers prefer dark mode?", "Because light attracts bugs! 🐛"),
        ("Why did the developer go broke?", "Because he used up all his cache! 💰"),
        ("What's a programmer's favorite hangout?", "The Foo Bar! 🍺"),
        ("Why do Java developers wear glasses?", "Because they can't C#! 👓"),
        ("How many programmers does it take to change a light bulb?", "None, that's a hardware problem! 💡"),
    ]
    
    setup, punchline = random.choice(jokes)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="😂 Another One!", callback_data="fun_jokes"),
        InlineKeyboardButton(text="🔙 Back", callback_data="module_fun")
    )
    
    text = f"""
😂 <b>Here's a Joke!</b>

<b>Q:</b> {setup}

<b>A:</b> {punchline}

Hope that made you smile! 😄
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "fun_poem")
async def generate_poem(callback: CallbackQuery):
    """Generate a random poem"""
    poems = [
        """
✍️ <b>Ode to Code</b>

In lines of code, we find our art,
Each function plays its vital part,
With loops and if's, we build our dreams,
Creating worlds with data streams.

Debugging late into the night,
Until our program works just right,
The joy we feel when tests turn green,
The best reward we've ever seen!
""",
        """
✍️ <b>The Developer's Journey</b>

From "Hello World" we all begin,
A simple print, our first small win,
We learn and grow with every line,
Our skills improve with passing time.

Through errors, bugs, and endless tests,
We persevere and do our best,
For in this craft, we find our way,
Building tomorrow, today!
"""
    ]
    
    poem = random.choice(poems)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✍️ Another Poem", callback_data="fun_poem"),
        InlineKeyboardButton(text="🔙 Back", callback_data="module_fun")
    )
    
    await callback.message.edit_text(poem, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "fun_quiz")
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    """Start quiz game"""
    questions = [
        {
            "q": "What does HTML stand for?",
            "options": ["Hyper Text Markup Language", "High Tech Modern Language", "Home Tool Markup Language", "Hyperlinks and Text Markup Language"],
            "correct": 0
        },
        {
            "q": "Which programming language is known as the 'language of the web'?",
            "options": ["Python", "JavaScript", "Java", "C++"],
            "correct": 1
        },
        {
            "q": "What year was Python first released?",
            "options": ["1989", "1991", "1995", "2000"],
            "correct": 1
        }
    ]
    
    question = random.choice(questions)
    await state.update_data(correct_answer=question["correct"])
    
    builder = InlineKeyboardBuilder()
    for i, option in enumerate(question["options"]):
        builder.row(
            InlineKeyboardButton(text=option, callback_data=f"quiz_ans_{i}")
        )
    builder.row(
        InlineKeyboardButton(text="❌ Exit Quiz", callback_data="module_fun")
    )
    
    text = f"""
🎮 <b>Quiz Time!</b>

<b>Question:</b>
{question['q']}

Choose the correct answer:
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await state.set_state(FunStates.playing_quiz)
    await callback.answer()


@router.callback_query(F.data.startswith("quiz_ans_"), FunStates.playing_quiz)
async def check_quiz_answer(callback: CallbackQuery, state: FSMContext):
    """Check quiz answer"""
    user_answer = int(callback.data.split("_")[-1])
    data = await state.get_data()
    correct = data.get("correct_answer", 0)
    
    if user_answer == correct:
        result = "✅ <b>Correct!</b> 🎉"
        emoji = "🎊"
    else:
        result = "❌ <b>Incorrect!</b>"
        emoji = "😅"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎮 Play Again", callback_data="fun_quiz"),
        InlineKeyboardButton(text="🔙 Back", callback_data="module_fun")
    )
    
    text = f"""
{result}

{emoji} Keep playing to improve your score!

<b>Your Stats:</b>
• Questions Answered: 1
• Correct: {1 if user_answer == correct else 0}
• Accuracy: {100 if user_answer == correct else 0}%
"""
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "fun_riddle")
async def show_riddle(callback: CallbackQuery):
    """Show a riddle"""
    riddles = [
        ("I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?", "An echo"),
        ("The more you take, the more you leave behind. What am I?", "Footsteps"),
        ("What has keys but no locks, space but no room, and you can enter but can't go inside?", "A keyboard"),
        ("I'm tall when I'm young, and I'm short when I'm old. What am I?", "A candle"),
    ]
    
    riddle, answer = random.choice(riddles)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💡 Show Answer", callback_data=f"riddle_ans"),
        InlineKeyboardButton(text="🎲 Another Riddle", callback_data="fun_riddle")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="module_fun")
    )
    
    # Store answer in callback data (simplified)
    await callback.message.edit_text(
        f"🎲 <b>Riddle Time!</b>\n\n{riddle}\n\nCan you solve it?",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "fun_facts")
async def show_fun_fact(callback: CallbackQuery):
    """Show a fun fact"""
    facts = [
        "🌍 The first computer programmer was a woman named Ada Lovelace in the 1840s!",
        "🐛 The first computer bug was an actual bug - a moth found in a computer in 1947!",
        "💾 The first 1GB hard drive weighed over 500 pounds and cost $40,000!",
        "🖥️ The first computer mouse was made of wood!",
        "📧 The first email was sent in 1971 by Ray Tomlinson to himself!",
        "🌐 The first website is still online: http://info.cern.ch/",
        "💻 The first computer virus was created in 1983 and was called 'Elk Cloner'!",
    ]
    
    fact = random.choice(facts)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💡 Another Fact", callback_data="fun_facts"),
        InlineKeyboardButton(text="🔙 Back", callback_data="module_fun")
    )
    
    await callback.message.edit_text(
        f"💡 <b>Fun Fact!</b>\n\n{fact}",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "fun_roast")
async def roast_user(callback: CallbackQuery):
    """Friendly roast"""
    roasts = [
        "Your code is so clean, even Marie Kondo would be proud! (Just kidding, we both know it's a mess 😄)",
        "I've seen better variable names in a random string generator! 😂",
        "Your Git commits are like your New Year's resolutions - full of good intentions but rarely followed through! 🎯",
        "You're the type of developer who comments 'TODO: Fix this later' and 'later' never comes! ⏰",
        "Your code has more bugs than a rainforest! 🐛🌳",
    ]
    
    roast = random.choice(roasts)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎭 Roast Me Again!", callback_data="fun_roast"),
        InlineKeyboardButton(text="🔙 Back", callback_data="module_fun")
    )
    
    await callback.message.edit_text(
        f"🎭 <b>Friendly Roast!</b>\n\n{roast}\n\n<i>All in good fun! 😊</i>",
        reply_markup=builder.as_markup()
    )
    await callback.answer()
