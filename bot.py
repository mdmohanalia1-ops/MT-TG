import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InputPhoneContact
from pyrogram.errors import FloodWait, RPCError, SessionPasswordNeeded

# --- CONFIGURATION ---
api_id = 39166101
api_hash = "2d509c626345ddaa73aff7cf4abde9bf"
bot_token = "8690395871:AAGdnjesF0cAzV6jYk63Go5AuZiM0QmfxmE"
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

# --- START COMMAND & APPROVAL ---
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    if not is_approved(user_id):
        await message.reply_text("🚫 আপনার এই বট ব্যবহারের অনুমতি নেই। আপনার রিকোয়েস্ট এডমিনের কাছে পাঠানো হয়েছে।")
        await client.send_message(
            ADMIN_ID, 
            f"🔔 **নতুন ইউজার রিকোয়েস্ট!**\n\nনাম: {message.from_user.first_name}\nইউজার আইডি: `{user_id}`", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve User", callback_data=f"approve_{user_id}")]])
        )
        return
    
    keyboard = ReplyKeyboardMarkup(
        [["➕ সেশন যোগ করুন", "📊 আমার স্ট্যাটাস"], ["📤 সেশন লগআউট", "🔄 সেশন রিসেট"], ["📝 ফরম্যাট নম্বর"]], 
        resize_keyboard=True
    )
    await message.reply_text(f"স্বাগতম **{message.from_user.first_name}**! 🤖\nবট এখন ব্যবহারের জন্য প্রস্তুত।", reply_markup=keyboard)

@app.on_callback_query(filters.regex("^approve_"))
async def approve_handler(client, callback_query):
    if callback_query.from_user.id != ADMIN_ID: return
    target_id = callback_query.data.split("_")[1]
    
    with open(APPROVED_USERS_FILE, "a") as f: 
        f.write(f"{target_id}\n")
    
    await callback_query.edit_message_text(f"✅ ইউজার `{target_id}` অনুমোদিত হয়েছে।")
    try:
        await client.send_message(int(target_id), "🎉 অভিনন্দন! এডমিন আপনাকে বট ব্যবহারের অনুমতি দিয়েছে। এখন /start দিন।")
    except:
        pass

# --- SESSION LOGOUT ---
@app.on_message(filters.regex("^📤 সেশন লগআউট$") & filters.private)
async def logout_menu(client, message):
    user_id = message.from_user.id
    if not is_approved(user_id): return
    session_file = get_user_session_file(user_id)
    if not os.path.exists(session_file):
        await message.reply_text("কোন সেশন পাওয়া যায়নি।")
        return
    with open(session_file, "r") as f: 
        lines = [l.strip() for l in f.readlines() if l.strip()]
    
    if not lines:
        await message.reply_text("সেশন লিস্ট খালি।")
        return

    btn_list = [[InlineKeyboardButton(f"❌ Logout: {line.split('|')[1]}", callback_data=f"del_{i}")] for i, line in enumerate(lines)]
    await message.reply_text("কোন সেশনটি লগআউট করতে চান?", reply_markup=InlineKeyboardMarkup(btn_list))

@app.on_callback_query(filters.regex("^del_"))
async def delete_session_callback(client, callback_query):
    user_id = callback_query.from_user.id
    idx = int(callback_query.data.split("_")[1])
    session_file = get_user_session_file(user_id)
    if os.path.exists(session_file):
        with open(session_file, "r") as f: lines = f.readlines()
        if idx < len(lines):
            lines.pop(idx)
            with open(session_file, "w") as f: f.writelines(lines)
            await callback_query.edit_message_text("✅ সেশনটি লিস্ট থেকে সফলভাবে সরানো হয়েছে।")

# --- MAIN HANDLER ---
@app.on_message(filters.text & filters.private)
async def handle_all(client, message):
    user_id = message.from_user.id
    if not is_approved(user_id): return
    text = message.text
    session_file = get_user_session_file(user_id)

    # বাটন কমান্ড চেক
    if text == "➕ সেশন যোগ করুন":
        user_steps[user_id] = {"step": "phone"}
        await message.reply_text("টেলিগ্রাম নাম্বারটি দিন (অবশ্যই + সহ):")
        return
    elif text == "📊 আমার স্ট্যাটাস":
        if user_id in user_steps: del user_steps[user_id]
        count = sum(1 for line in open(session_file)) if os.path.exists(session_file) else 0
        await message.reply_text(f"📊 আপনার নিজস্ব মোট সেশন: {count}টি")
        return
    elif text == "🔄 সেশন রিসেট":
        if user_id in user_steps: del user_steps[user_id]
        if os.path.exists(session_file): os.remove(session_file)
        await message.reply_text("✅ আপনার সব সেশন মুছে ফেলা হয়েছে।")
        return
    elif text == "📝 ফরম্যাট নম্বর":
        if user_id in user_steps: del user_steps[user_id]
        await message.reply_text("📝 **নাম্বার ফরম্যাট:**\n\nঅবশ্যই + চিহ্ন দিয়ে শুরু করবেন। একাধিক নাম্বার হলে নিচে নিচে দিন।\n\nউদাহরণ:\n`+27123456789` \n`+27987654321`")
        return

    # লগইন প্রসেস
    if user_id in user_steps:
        step = user_steps[user_id].get("step")
        if step == "phone":
            phone = text.replace(" ", "")
            await message.reply_text(f"🔄 {phone} এ কোড পাঠানো হচ্ছে...")
            try:
                temp_client = Client(f"temp_{user_id}", api_id=api_id, api_hash=api_hash, in_memory=True,
                                     device_model="Desktop", system_version="Windows 10", app_version="4.16.8")
                await temp_client.connect()
                code_info = await temp_client.send_code(phone)
                user_steps[user_id].update({"client": temp_client, "phone": phone, "hash": code_info.phone_code_hash, "step": "otp"})
                await message.reply_text("✅ কোড পাঠানো হয়েছে। আপনার টেলিগ্রাম অ্যাপ চেক করে কোডটি দিন:")
            except Exception as e:
                await message.reply_text(f"❌ এরর: {str(e)}"); del user_steps[user_id]
            return
        elif step == "otp":
            otp = text.replace(" ", ""); data = user_steps[user_id]
            try:
                await data["client"].sign_in(data["phone"], data["hash"], otp)
                await finish_login(message, data, user_id)
            except SessionPasswordNeeded:
                user_steps[user_id].update({"step": "password"})
                await message.reply_text("🔐 ২-স্টেপ পাসওয়ার্ড আছে। পাসওয়ার্ডটি দিন:")
            except Exception as e:
                await message.reply_text(f"❌ এরর: {str(e)}"); del user_steps[user_id]
            return
        elif step == "password":
            pwd = text; data = user_steps[user_id]
            try:
                await data["client"].check_password(pwd)
                await finish_login(message, data, user_id)
            except Exception as e:
                await message.reply_text(f"❌ ভুল পাসওয়ার্ড: {str(e)}"); del user_steps[user_id]
            return

    # নাম্বার চেকিং
    elif text.startswith("+"):
        if not os.path.exists(session_file):
            await message.reply_text("❌ আপনার সেশন নেই! আগে সেশন যোগ করুন।")
            return
        with open(session_file, "r") as f: all_lines = [l.strip() for l in f if l.strip()]
        sessions = [l.split("|")[0] for l in all_lines]
        numbers = [n.strip() for n in text.split('\n') if n.strip()]
        res_msg = await message.reply_text("⚙️ চেকিং শুরু হচ্ছে...")
        reg, unreg, s_idx = [], [], 0

        for idx, num in enumerate(numbers):
            cur_session = sessions[s_idx % len(sessions)]; s_idx += 1
            try:
                async with Client("checker", session_string=cur_session, api_id=api_id, api_hash=api_hash, in_memory=True) as worker:
                    result = await worker.import_contacts([InputPhoneContact(phone=num, first_name="Check")])
                    if result.users:
                        reg.append(num); await worker.delete_contacts([u.id for u in result.users])
                    else: unreg.append(num)
            except: unreg.append(num)

            # এখানেই লিমিট সরানো হয়েছে, এখন সবগুলো শো করবে
            report = (f"⚙️ **Checking...** ({idx+1}/{len(numbers)})\n━━━━━━━━━━━━━━━━━━\n✅ Reg: {len(reg)}\n❌ Non: {len(unreg)}\n━━━━━━━━━━━━━━━━━━\n")
            if reg: report += f"✅ **Reg:**\n" + "\n".join(reg) + "\n"
            if unreg: report += f"\n❌ **Non:**\n" + "\n".join(unreg) + "\n"
            
            try: await res_msg.edit_text(report)
            except: pass
            await asyncio.sleep(4)

        final_msg = (f"✅ **Check Completed**\n━━━━━━━━━━━━━━━━━━\n✅ Total: {len(reg)}\n❌ Total: {len(unreg)}\n━━━━━━━━━━━━━━━━━━\n\n✅ **Registered List:**\n" + ("\n".join(reg) if reg else "None") + "\n\n❌ **Non-Registered List:**\n" + ("\n".join(unreg) if unreg else "None"))
        await res_msg.edit_text(final_msg)

async def finish_login(message, data, user_id):
    me = await data["client"].get_me()
    session_str = await data["client"].export_session_string()
    with open(get_user_session_file(user_id), "a") as f: 
        f.write(f"{session_str}|{me.first_name} ({data['phone']})\n")
    await message.reply_text(f"🎉 সেশন সফলভাবে যুক্ত হয়েছে: {me.first_name}")
    await data["client"].disconnect()
    del user_steps[user_id]

if __name__ == "__main__":
    app.run()
