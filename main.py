import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from dotenv import load_dotenv

# .env फाइल से डेटा लोड करना
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
OWNER_ID = int(os.getenv("OWNER_ID"))  # Owner ID को int में कन्वर्ट करना

CHANNELS = ["@skillwithgaurav", "@skillcoursesfree"]  # चैनल्स लिस्ट

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["telegram_bot"]
users_collection = db["users"]
settings_collection = db["settings"]

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_welcome_message():
    settings = settings_collection.find_one({"_id": "welcome_message"})
    return settings["message"] if settings else "👋 Welcome to our bot!"

async def check_subscription(client, user_id):
    for channel in CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"

    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id, "username": username})
    
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ Joined", callback_data="joined")]]
    )

    channels_text = "\n".join([f"➡️ [Join {ch}](https://t.me/{ch.replace('@', '')})" for ch in CHANNELS])
    
    await message.reply(
        f"🔔 **Please join our channels first:**\n\n{channels_text}", 
        reply_markup=keyboard, 
        disable_web_page_preview=True
    )

@app.on_callback_query(filters.regex("joined"))
async def joined(client, callback_query):
    user_id = callback_query.from_user.id
    if await check_subscription(client, user_id):
        welcome_text = get_welcome_message()
        await callback_query.message.delete()
        
        sent_message = await client.send_message(user_id, welcome_text)
        await asyncio.sleep(5)

        delete_message = await client.send_message(
            user_id, 
            "⚠️ इस मैसेज को **फॉरवर्ड करके सेव** कर लें, क्योंकि **5 मिनट में ये डिलीट हो जाएगा!**"
        )
        await asyncio.sleep(300)  # 5 मिनट का टाइमर
        await delete_message.delete()
    else:
        await callback_query.answer("❌ पहले चैनल्स को जॉइन करें!", show_alert=True)

@app.on_message(filters.command("welcome") & filters.user(OWNER_ID))
async def set_welcome(client, message: Message):
    new_message = message.text.replace("/welcome ", "", 1)
    if new_message:
        settings_collection.update_one({"_id": "welcome_message"}, {"$set": {"message": new_message}}, upsert=True)
        await message.reply("✅ Welcome message updated!")
    else:
        await message.reply("❌ Please provide a welcome message!")

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client, message: Message):
    total_users = users_collection.count_documents({})
    await message.reply(f"📊 Total Users: **{total_users}**")

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message: Message):
    if len(message.text.split()) < 2:
        return await message.reply("❌ Usage: /broadcast [message]")

    broadcast_message = message.text.replace("/broadcast ", "", 1)
    users = users_collection.find({})
    sent, failed = 0, 0

    for user in users:
        try:
            await client.send_message(user["user_id"], broadcast_message)
            sent += 1
        except:
            failed += 1

    await message.reply(f"✅ Broadcast completed!\n📤 Sent: {sent}\n❌ Failed: {failed}")

@app.on_message(filters.command("users") & filters.user(OWNER_ID))
async def list_users(client, message: Message):
    users = users_collection.find({})
    user_list = "\n".join([f"🔹 @{user['username']} (ID: {user['user_id']})" for user in users if user['username'] != "No Username"])

    if user_list:
        await message.reply(f"👥 **Bot Users:**\n{user_list}")
    else:
        await message.reply("🚫 No users found.")

if __name__ == "__main__":
    print("🚀 Bot is running...")
    app.run()
