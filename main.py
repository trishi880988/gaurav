import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

CHANNELS = ["@skillcoursesfree", "https://t.me/+F6qoCTHt_b8xNjNl"]  # <-- Updated channels

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["telegram_bot"]
users_collection = db["users"]
settings_collection = db["settings"]

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_welcome_message():
    settings = settings_collection.find_one({"_id": "welcome_message"})
    return settings["message"] if settings else "👋 Welcome to our bot!"

async def is_user_joined(client, user_id):
    for channel in CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user_id = message.from_user.id
    
    if not await is_user_joined(client, user_id):
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Join Channel 1", url=f"https://t.me/{CHANNELS[0][1:]}")],
             [InlineKeyboardButton("Join Channel 2", url=f"https://t.me/{CHANNELS[1][1:]}")],
             [InlineKeyboardButton("✅ Joined", callback_data="check_join")]]
        )
        await message.reply("🔔 First join these channels to continue:", reply_markup=keyboard)
        return
    
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id})
    
    welcome_text = get_welcome_message()
    sent_message = await message.reply(welcome_text)
    await asyncio.sleep(600)
    await sent_message.delete()

@app.on_callback_query(filters.regex("check_join"))
async def check_join(client, callback_query):
    user_id = callback_query.from_user.id
    if await is_user_joined(client, user_id):
        await callback_query.message.delete()
        await start(client, callback_query.message)
    else:
        await callback_query.answer("❌ Please join all channels first!", show_alert=True)

app.run()
