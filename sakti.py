import asyncio
import aiohttp
from urllib.parse import urlparse, parse_qs
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# --- CONFIGURATION ---
API_TOKEN = '8469208952:AAEBogbi969MQ5XpXY_U_SoSmyHlLpWWzlE'
# GitHub Raw Link yahan dalein
TASKS_URL = 'https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/tasks.json'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def fetch_tasks():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(TASKS_URL) as resp:
                return await resp.json() if resp.status == 200 else []
    except: return []

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("👋 **Hello King**\n\nSend Foundit link to fire postbacks.")

@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    user_link = message.text
    tasks = await fetch_tasks()
    
    for t in tasks:
        parsed = urlparse(user_link)
        params = parse_qs(parsed.query)
        key = t['clickid_key']
        
        if key in params:
            clickid = params[key][0]
            results = []
            
            async with aiohttp.ClientSession() as session:
                for pb_pattern in t['postbacks']:
                    final_url = pb_pattern.replace("{clickid}", clickid)
                    try:
                        async with session.get(final_url, timeout=10) as resp:
                            if resp.status == 200:
                                results.append("✅ Success")
                            else:
                                results.append(f"❌ Failed")
                    except:
                        results.append("❌ Connection Error")
            
            # Postback link show nahi hoga, sirf status dikhayega
            status_text = "\n".join(results)
            await message.answer(
                f"🎯 **Task: {t['name']}**\n"
                f"🆔 ID: `{clickid}`\n\n"
                f"**Status:**\n{status_text}",
                parse_mode="Markdown"
            )
            return

    await message.answer("⚠️ Match Not Found! Check if link has 'cl=' parameter.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
