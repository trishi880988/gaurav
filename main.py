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

# Default Welcome Message
WELCOME_MESSAGE = """👋 **Welcome to our bot!**\n\n🚀 **Enjoy your time here!**\n\n📌 **Free Resources:**\n
📖 **Video book summary:** [Join Now](https://t.me/+3825pitGv5o5ZjU1)\n
📚 **10+ Paid Courses Free:** [Join Now](https://t.me/skillcoursesfree)\n
🎧 **200+ Audiobook Free:** [Join Now](https://t.me/+1yyJc4EWyU00Y2M1)\n
📺 **1000+ Movies:** [Join Now](https://t.me/+Rp1BJ_BKIHEzNzc1)\n
📚 **Rewire Course Free:** [Join Now](https://t.me/+82fYlfO3dzs2ZTNl)\n
📦 **700+ Course Bundle:** [Join Now](https://t.me/+X_WmbmYCX-ExZjRl)\n
🎓 **700+ Single Course:** [Join Now](https://t.me/+F6qoCTHt_b8xNjNl)\n
🎤 **New Audio Book Channel:** [Join Now](https://t.me/+3gjdANs7XYdjODVl)\n
🎬 **400+ GB Video Editing Assets:** [Join Now](https://t.me/+ib09i2lV0IplMTNl)\n
🎭 **Exclusive Content:** [Join Now](https://t.me/samayrainahu)\n
🔄 **Backup Channel:** [Join Now](https://t.me/+Sr-q-iV8Pi5jMTBl)\n
📖 **Acharya Prashant:** [Join Now](https://t.me/+ejX2w0DP1nE5MGJl)\n
🤖 **Dhruv Rathee ChatGPT Course:** [Join Now](https://t.me/skillozone/2)\n
🎥 **Dhruv Rathee YouTube Blueprint Course:** [Join Now](https://t.me/skillozone/45)\n
📖 **Dhruv Rathee Ebook:** [Join Now](https://t.me/+m2wR766h8TcxYjU1)\n
🎨 **Deepak Daiya Thumbnail Editing Course:** [Join Now](https://t.me/+vLbFATtijG4zNzZl)\n
🔮 **Advance Law of Attraction Course:** [Join Now](https://t.me/skillcoursesfree/788)\n
🎬 **Storytelling Video Editing Course:** [Join Now](https://t.me/skillcoursesfree/784)\n
🗣 **Alina Rais English Speaking Course:** [Join Now](https://t.me/skillcoursesfree/782)\n"""

# स्टोर किया गया वेलकम मैसेज
stored_welcome_message = WELCOME_MESSAGE

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user_id = message.from_user.id
    sent_message = await client.send_message(user_id, stored_welcome_message, disable_web_page_preview=True)

    # 30 मिनट (1800 सेकंड) बाद मैसेज हटाने के लिए डिले सेट करें
    await asyncio.sleep(1800)
    await client.delete_messages(user_id, sent_message.message_id)

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
    while True:  # 🔄 बॉट कभी बंद नहीं होगा
        try:
            app.run()
        except Exception as e:
            print(f"⚠️ Error occurred: {e}, restarting bot...")
