import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters, idle
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# --- RENDER PORT FIX ---
PORT = int(os.environ.get("PORT", 8080))

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Live!")

def run_health_check():
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check, daemon=True).start()

# --- CONFIGURATION (Environment variables preference) ---
api_id = int(os.environ.get("API_ID", 39166101))
api_hash = os.environ.get("API_HASH", "2d509c626345ddaa73aff7cf4abde9bf")
bot_token = os.environ.get("BOT_TOKEN", "8690395871:AAGdnjesF0cAzV6jYk63Go5AuZiM0QmfxmE")
ADMIN_ID = 8385150965
APPROVED_USERS_FILE = "approved_users.txt"

app = Client("my_bot_session", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def is_approved(user_id):
    if user_id == ADMIN_ID: return True
    if not os.path.exists(APPROVED_USERS_FILE): return False
    with open(APPROVED_USERS_FILE, "r") as f:
        approved_list = f.read().splitlines()
    return str(user_id) in approved_list

# --- COMMANDS ---
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    if not is_approved(user_id):
        await message.reply_text("🚫 আপনার অনুমতি নেই।")
        return
    
    keyboard = ReplyKeyboardMarkup(
        [["📊 আমার স্ট্যাটাস", "🔄 সেশন রিসেট"]], 
        resize_keyboard=True
    )
    await message.reply_text("✅ বট সচল আছে!", reply_markup=keyboard)

# --- MAIN EXECUTION ---
async def main():
    await app.start()
    print("🚀 Bot is Live!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    app.run(main())
