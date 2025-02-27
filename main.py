import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

# .env फाइल से डेटा लोड करना
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))  # Owner ID को int में कन्वर्ट करना

# Default Welcome Message (अगर नया सेट नहीं किया गया)
WELCOME_MESSAGE = "👋 Welcome to our bot!\n\n🚀 Enjoy your time here!"

# स्टोर किया गया वेलकम मैसेज
stored_welcome_message = WELCOME_MESSAGE

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user_id = message.from_user.id

    # वेलकम मैसेज भेजना
    sent_message = await client.send_message(user_id, stored_welcome_message)
    await asyncio.sleep(5)

    # डिलीट होने का नोटिफिकेशन भेजना
    delete_message = await client.send_message(
        user_id, "⚠️ इस मैसेज को **फॉरवर्ड करके सेव** कर लें, क्योंकि **5 मिनट में ये डिलीट हो जाएगा!**"
    )

    await asyncio.sleep(300)  # 5 मिनट का टाइमर
    await delete_message.delete()

@app.on_message(filters.command("setwelcome") & filters.user(OWNER_ID))
async def set_welcome(client, message: Message):
    global stored_welcome_message

    new_message = message.text.replace("/setwelcome ", "", 1)
    
    if new_message:
        stored_welcome_message = new_message
        await message.reply("✅ **Welcome message updated!**")
    else:
        await message.reply("❌ **Please provide a new welcome message!**")

if __name__ == "__main__":
    print("🚀 Bot is running...")
    app.run()
