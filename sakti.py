import sqlite3
import asyncio
import aiohttp
from urllib.parse import urlparse, parse_qs
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# --- CONFIGURATION ---
API_TOKEN = '8469208952:AAEBogbi969MQ5XpXY_U_SoSmyHlLpWWzlE'
ADMIN_ID = 6651927363

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('postback.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (name TEXT, url_pattern TEXT, clickid_key TEXT, example_link TEXT)''')
    conn.commit()
    conn.close()

# --- STATES ---
class TaskForm(StatesGroup):
    name = State()
    url = State()
    clickid_key = State()
    example = State()

# --- ADMIN COMMANDS ---

@dp.message(Command("add"), F.from_user.id == ADMIN_ID)
async def add_task(message: types.Message, state: FSMContext):
    await message.answer("🛠 *Admin Mode*\nStep 1: Task का नाम भेजें (जैसे: Winzo)")
    await state.set_state(TaskForm.name)

@dp.message(TaskForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Step 2: Postback URL भेजें।\nजहाँ ID आनी है वहां `{clickid}` लिखें।\n\nExample: `https://site.com/pb?cid={clickid}`")
    await state.set_state(TaskForm.url)

@dp.message(TaskForm.url)
async def process_url(message: types.Message, state: FSMContext):
    await state.update_data(url=message.text)
    await message.answer("Step 3: ClickID की Key भेजें।\n(अगर लिंक में `&aff_id=123` है, तो `aff_id` लिखें)")
    await state.set_state(TaskForm.clickid_key)

@dp.message(TaskForm.clickid_key)
async def process_key(message: types.Message, state: FSMContext):
    await state.update_data(clickid_key=message.text)
    await message.answer("Step 4: यूज़र्स के लिए एक Example लिंक भेजें।")
    await state.set_state(TaskForm.example)

@dp.message(TaskForm.example)
async def process_example(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conn = sqlite3.connect('postback.db')
    c = conn.cursor()
    c.execute("INSERT INTO tasks VALUES (?, ?, ?, ?)", 
              (data['name'], data['url'], data['clickid_key'], message.text))
    conn.commit()
    conn.close()
    await message.answer(f"✅ Task '{data['name']}' सफलतापूर्वक सेव हो गया!")
    await state.clear()

# --- USER LOGIC ---

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    conn = sqlite3.connect('postback.db')
    c = conn.cursor()
    c.execute("SELECT name, example_link FROM tasks")
    tasks = c.fetchall()
    conn.close()

    text = "👋 स्वागत है! अपना लिंक भेजें और मैं पोस्टबैक हिट कर दूँगा।\n\n*मौजूदा टास्क:*\n"
    if not tasks:
        text += "अभी कोई टास्क ऐड नहीं है।"
    for t in tasks:
        text += f"🔹 {t[0]} (Example: `{t[1]}`)\n"
    
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    user_link = message.text
    conn = sqlite3.connect('postback.db')
    c = conn.cursor()
    c.execute("SELECT name, url_pattern, clickid_key FROM tasks")
    tasks = c.fetchall()
    conn.close()

    for name, pattern, key in tasks:
        parsed = urlparse(user_link)
        params = parse_qs(parsed.query)
        
        if key in params:
            clickid = params[key][0]
            final_url = pattern.replace("{clickid}", clickid)
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(final_url, timeout=10) as resp:
                        status = resp.status
                await message.answer(f"✅ {name} Postback Fired!\nID: `{clickid}`\nStatus: {status}", parse_mode="Markdown")
                return
            except Exception as e:
                await message.answer(f"❌ Error: {str(e)}")
                return
    
    await message.answer("⚠️ यह लिंक किसी भी टास्क से मैच नहीं हुआ।")

async def main():
    init_db()
    print("Bot is Starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
            
