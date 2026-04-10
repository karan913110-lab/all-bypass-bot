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

# Render पर सीधा कनेक्शन काम करता है (No Proxy Needed)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (name TEXT, url_pattern TEXT, clickid_key TEXT, example_link TEXT)''')
    conn.commit()
    conn.close()

# --- बाकी सारा लॉजिक (States, add_task, handle_link) यहाँ रहेगा ---
# (Handle_link में aiohttp.get() से 'proxy' पैरामीटर हटा दें)

async def main():
    init_db()
    print("Bot is LIVE on Render!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
