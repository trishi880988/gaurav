import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB connection
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["telegram_bot"]
users_collection = db["users"]
settings_collection = db["settings"]

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ⬇️ Helper function to get welcome message
def get_welcome_message():
    settings = settings_collection.find_one({"_id": "welcome_message"})
    return settings["message"] if settings else "👋 Welcome to our bot!"

# ⬇️ Command to set welcome message (Admin only)
@app.on_message(filters.command("setwelcome") & filters.user(ADMIN_ID))
async def set_welcome(client, message: Message):
    new_message = message.text.split("/setwelcome", maxsplit=1)[-1].strip()
    if not new_message:
        await message.reply("❌ Please provide a welcome message.")
        return

    settings_collection.update_one({"_id": "welcome_message"}, {"$set": {"message": new_message}}, upsert=True)
    await message.reply("✅ Welcome message updated successfully!")

# ⬇️ Start command - Send welcome message
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user_id = message.from_user.id
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id})

    welcome_text = get_welcome_message()
    sent_message = await message.reply(welcome_text)

    # Auto-delete message after 10 minutes
    await asyncio.sleep(600)
    await sent_message.delete()

# ⬇️ Command to get stats (Admin only)
@app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats(client, message: Message):
    total_users = users_collection.count_documents({})
    await message.reply(f"📊 Total Users: {total_users}")

# ⬇️ Command to broadcast message to all users (Admin only)
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast(client, message: Message):
    text = message.text.split("/broadcast", maxsplit=1)[-1].strip()
    if not text:
        await message.reply("❌ Please provide a message to broadcast.")
        return

    users = users_collection.find()
    sent_count = 0
    failed_count = 0

    for user in users:
        try:
            await client.send_message(user["user_id"], text)
            sent_count += 1
        except Exception:
            failed_count += 1

    await message.reply(f"✅ Broadcast completed!\nSent: {sent_count} users\nFailed: {failed_count} users.")

app.run()
