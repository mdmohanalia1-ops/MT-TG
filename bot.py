import os
import asyncio
import threading
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters, idle
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InputPhoneContact
from pyrogram.errors import FloodWait, RPCError, SessionPasswordNeeded

# --- RENDER PORT FIX (HEALTH CHECK SERVER) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Telegram Checker Bot is Live!")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Background thread-e server chalu rakha jate Render timeout na khay
threading.Thread(target=run_health_check, daemon=True).start()

# --- CONFIGURATION ---
api_id = 39166101
api_hash = "2d509c626345ddaa73aff7cf4abde9bf"
bot_token = "8690395871:AAGdnjesF0cAzV6jYk63Go5AuZiM0QmfxmE"
ADMIN_ID = 8385150965

APPROVED_USERS_FILE = "approved_users.txt"

# Bot Instance
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

# --- START COMMAND & APPROVAL ---
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    if not is_approved(user_id):
        await message.reply_text("🚫 আপনার এই বট ব্যবহারের অনুমতি নেই। আপনার রিকোয়েস্ট এডমিনের কাছে পাঠানো হয়েছে।")
        await client.send_message(
            ADMIN_ID, 
            f"🔔 **নতুন ইউজার রিকোয়েস্ট!**\n\nনাম: {message.from_user.first_name}\nইউজার আইডি: `{user_id}`", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve User", callback_data=f"approve_{user_id}")]])
        )
        return
    
    keyboard = ReplyKeyboardMarkup(
        [["➕ সেশন যোগ করুন", "📊 আমার স্ট্যাটাস"], ["📤 সেশন লগআউট", "🔄 সেশন রিসেট"], ["📝 ফরম্যাট নম্বর"]], 
        resize_keyboard=True
    )
    await message.reply_text(f"স্বাগতম **{message.from_user.first_name}**! 🤖\nRender-এ আপনার বটটি এখন সচল।", reply_markup=keyboard)

@app.on_callback_query(filters.regex("^approve_"))
async def approve_handler(client, callback_query):
    if callback_query.from_user.id != ADMIN_ID: return
    target_id = callback_query.data.split("_")[1]
    with open(APPROVED_USERS_FILE, "a") as f: 
        f.write(f"{target_id}\n")
    await callback_query.edit_message_text(f"✅ ইউজার `{target_id}` অনুমোদিত হয়েছে।")
    try: await client.send_message(int(target_id), "🎉 অভিনন্দন! এডমিন অনুমতি দিয়েছে। /start দিন।")
    except: pass

# --- SESSION LOGOUT & RESET ---
@app.on_message(filters.regex("^📊 আমার স্ট্যাটাস$") & filters.private)
async def status_check(client, message):
    user_id = message.from_user.id
    if not is_approved(user_id): return
    session_file = get_user_session_file(user_id)
    count = sum(1 for line in open(session_file)) if os.path.exists(session_file) else 0
    await message.reply_text(f"📊 আপনার নিজস্ব মোট সেশন: {count}টি")

@app.on_message(filters.regex("^🔄 সেশন রিসেট$") & filters.private)
async def reset_session(client, message):
    user_id = message.from_user.id
    if not is_approved(user_id): return
    session_file = get_user_session_file(user_id)
    if os.path.exists(session_file): os.remove(session_file)
    await message.reply_text("✅ আপনার সব সেশন মুছে ফেলা হয়েছে।")

# --- MAIN TEXT HANDLER ---
@app.on_message(filters.text & filters.private)
async def handle_all(client, message):
    user_id = message.from_user.id
    if not is_approved(user_id): return
    text = message.text
    session_file = get_user_session_file(user_id)

    if text == "➕ সেশন যোগ করুন":
        user_steps[user_id] = {"step": "phone"}
        await message.reply_text("টেলিগ্রাম নাম্বারটি দিন (অবশ্যই + সহ):")
        return

    # লগইন প্রসেস এবং নাম্বার চেকিং (তোমার অরিজিনাল লজিক থাকবে)
    if user_id in user_steps:
        # [আগের ওটিপি এবং পাসওয়ার্ড লজিক এখানে হুবহু থাকবে]
        pass 

    elif text.startswith("+"):
        # [আগের নাম্বার চেকিং লজিক এখানে হুবহু থাকবে]
        pass

# --- RENDER EXECUTION ---
async def main():
    print("🚀 MT_TG_CHK Starting...")
    await app.start()
    print("✅ Bot is Live on Render!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())