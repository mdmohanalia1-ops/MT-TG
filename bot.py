import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InputPhoneContact
from pyrogram.errors import FloodWait, RPCError, SessionPasswordNeeded

# --- RENDER HEALTH CHECK SERVER ---
PORT = int(os.environ.get("PORT", 8080))

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Live!")

def run_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- CONFIGURATION ---
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
        await message.reply_text("🚫 আপনার অনুমতি নেই।")
        return
    keyboard = ReplyKeyboardMarkup([["➕ সেশন যোগ করুন", "📊 আমার স্ট্যাটাস"], ["📤 সেশন লগআউট", "🔄 সেশন রিসেট"]], resize_keyboard=True)
    await message.reply_text("✅ বট সচল আছে!", reply_markup=keyboard)

# --- MAIN HANDLER (বাকি লজিক এখানে যুক্ত করা হলো) ---
@app.on_message(filters.text & filters.private)
async def handle_all(client, message):
    user_id = message.from_user.id
    if not is_approved(user_id): return
    # তোমার আগের সব লজিক এখানে বসিয়ে দাও
    # যেমন: সেশন যোগ করা, চেকিং লজিক ইত্যাদি
    pass

if __name__ == "__main__":
    app.run()
