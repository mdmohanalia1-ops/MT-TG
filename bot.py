import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InputPhoneContact
from pyrogram.errors import FloodWait, RPCError, SessionPasswordNeeded

# --- RENDER PORT FIX (HEALTH CHECK SERVER) ---
PORT = int(os.environ.get("PORT", 8080))

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Telegram Checker Bot is Live!")

def run_health_check():
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    server.serve_forever()

# ব্যাকগ্রাউন্ডে সার্ভার সচল রাখা
threading.Thread(target=run_health_check, daemon=True).start()

# --- CONFIGURATION ---
# Render-এর Environment Variables থেকে ডাটা নিবে, না থাকলে ডিফল্ট হিসেবে তোমার দেওয়া ভ্যালু ব্যবহার করবে
api_id = int(os.environ.get("API_ID", 39166101))
api_hash = os.environ.get("API_HASH", "2d509c626345ddaa73aff7cf4abde9bf")
bot_token = os.environ.get("BOT_TOKEN", "8690395871:AAGdnjesF0cAzV6jYk63Go5AuZiM0QmfxmE")
ADMIN_ID = 8385150965

APPROVED_USERS_FILE = "approved_users.txt"

app = Client("MT_TG_CHK", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
user_steps = {}

def get_user_session_file(user_id):
    return f"sessions_{user_id}.txt"

def is_approved(user_id):
    if user_id == ADMIN_ID: return True
    if not os.path.exists(APPROVED_USERS_FILE): return False
    with open(APPROVED_USERS_FILE, "r") as f:
        approved_list = f.read().splitlines()
    return str(user_id) in approved_list

# --- START COMMAND ---
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    if not is_approved(user_id):
        await message.reply_text("🚫 আপনার এই বট ব্যবহারের অনুমতি নেই।")
        return
    
    keyboard = ReplyKeyboardMarkup(
        [["➕ সেশন যোগ করুন", "📊 আমার স্ট্যাটাস"], ["📤 সেশন লগআউট", "🔄 সেশন রিসেট"], ["📝 ফরম্যাট নম্বর"]], 
        resize_keyboard=True
    )
    await message.reply_text(f"স্বাগতম **{message.from_user.first_name}**! 🤖\nবট এখন ব্যবহারের জন্য প্রস্তুত।", reply_markup=keyboard)

# --- লজিক সেকশন (তোমার অরিজিনাল লজিক অপরিবর্তিত) ---
# (এখানে তুমি তোমার আগের কোডের লগআউট, হ্যান্ডলার এবং চেকিং লজিকগুলো হুবহু বসিয়ে দাও)
# কোডের বাকি অংশগুলো আগের মতোই কাজ করবে।

async def finish_login(message, data, user_id):
    me = await data["client"].get_me()
    session_str = await data["client"].export_session_string()
    with open(get_user_session_file(user_id), "a") as f: 
        f.write(f"{session_str}|{me.first_name} ({data['phone']})\n")
    await message.reply_text(f"🎉 সেশন সফলভাবে যুক্ত হয়েছে: {me.first_name}")
    await data["client"].disconnect()
    del user_steps[user_id]

if __name__ == "__main__":
    app.run()
