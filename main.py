import os
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid
import asyncio

# Load environment variables
API_ID = int(os.getenv("API_ID"))  
API_HASH = os.getenv("API_HASH"))  
BOT_TOKEN = os.getenv("BOT_TOKEN"))  
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  

# Initialize the bot
bot = Client("movie_search_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("👋 Welcome! Send me a movie name, and I'll find it in our channel.")

@bot.on_message(filters.text & filters.private)
def search_movie(client, message):
    query = message.text.lower()
    print(f"Searching for: {query}")
    
    try:
        # Search in channel
        for msg in client.search_messages(CHANNEL_ID, query, limit=10):
            if msg.video or msg.document:
                file_id = msg.video.file_id if msg.video else msg.document.file_id
                
                # Send movie to user with warning message
                sent_msg = message.reply_video(
                    video=file_id, 
                    caption=f"🎬 Here is your movie: {msg.caption}\n\n⚠️ This file will be deleted in **30 minutes**. Please save or forward it!"
                )

                # Schedule message deletion after 30 minutes
                client.loop.call_later(1800, asyncio.create_task, delete_message(client, message.chat.id, sent_msg.message_id))

                return
        
        message.reply_text("❌ Movie not found. Try a different name!")
    except PeerIdInvalid:
        message.reply_text("❌ Bot is not an admin in the channel!")

async def delete_message(client, chat_id, message_id):
    try:
        await client.delete_messages(chat_id, message_id)
        await client.send_message(chat_id, "🗑️ File deleted! Next time, save or forward it quickly.")
    except Exception as e:
        print(f"Error deleting message: {e}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.run()
