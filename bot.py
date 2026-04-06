import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json, os

# ===== SECRETS =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

USERS = "users.json"
BANNED = "banned.json"

sent_messages = {}

# ===== UTILS =====
def load(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# ===== START UI =====
@bot.message_handler(commands=['start'])
def start(m):
    users = load(USERS)

    if m.from_user.id not in users:
        users.append(m.from_user.id)
        save(USERS, users)

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📩 Message Admin", callback_data="msg"),
        InlineKeyboardButton("📊 My Profile", callback_data="me"),
        InlineKeyboardButton("ℹ️ Help", callback_data="help")
    )

    text = f"""
<b>╭━━━〔 🔥 SUPPORT SYSTEM 〕━━━╮</b>

👋 Welcome <b>{m.from_user.first_name}</b>

💬 Talk directly with Admin  
⚡ Fast replies  
🔒 Private system  

<b>╰━━━━━━━━━━━━━━━━━━━━━━╯</b>

✨ Choose below:
"""
    bot.send_message(m.chat.id, text, reply_markup=kb)

# ===== BUTTONS =====
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if c.data == "msg":
        bot.send_message(c.message.chat.id, "✍️ Send your message now...")

    elif c.data == "help":
        bot.send_message(c.message.chat.id, "📌 Just send anything, admin will reply!")

    elif c.data == "me":
        bot.send_message(
            c.message.chat.id,
            f"👤 Name: {c.from_user.first_name}\n🆔 ID: <code>{c.from_user.id}</code>"
        )

# ===== USER → ADMIN =====
@bot.message_handler(func=lambda m: True,
content_types=['text','photo','video','document','audio','voice','sticker'])
def forward(m):
    if m.chat.id == ADMIN_ID:
        return

    banned = load(BANNED)
    if m.from_user.id in banned:
        return

    users = load(USERS)
    if m.from_user.id not in users:
        users.append(m.from_user.id)
        save(USERS, users)

    uid = m.from_user.id
    uname = m.from_user.username or "NoUsername"

    header = f"""
<b>╭━━━〔 📩 NEW MESSAGE 〕━━━╮</b>

👤 @{uname}
🆔 <code>{uid}</code>

━━━━━━━━━━━━━━━━━━━━━━
"""

    if m.content_type == "text":
        bot.send_message(ADMIN_ID, header + f"💬 {m.text}\n<b>╰━━━━━━━━━━━━━━━━━━━━━━╯</b>")
    else:
        bot.copy_message(ADMIN_ID, m.chat.id, m.message_id)
        bot.send_message(ADMIN_ID, header + "📎 Media\n<b>╰━━━━━━━━━━━━━━━━━━━━━━╯</b>")

# ===== ADMIN REPLY =====
@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.reply_to_message,
content_types=['text','photo','video','document','audio','voice','sticker'])
def reply(m):
    try:
        text = m.reply_to_message.text
        uid = int(text.split("🆔 ")[1].split("\n")[0])

        sent = bot.copy_message(uid, m.chat.id, m.message_id)
        sent_messages[sent.message_id] = uid

        bot.reply_to(m, "✅ Sent")
    except:
        bot.reply_to(m, "❌ Failed")

# ===== SEEN SYSTEM =====
@bot.message_handler(func=lambda m: True)
def seen(m):
    uid = m.from_user.id

    for msg_id, user in list(sent_messages.items()):
        if user == uid:
            bot.send_message(ADMIN_ID, f"""
<b>╭━━━〔 👁️ SEEN STATUS 〕━━━╮</b>

✅ User seen your message  
🆔 <code>{uid}</code>

<b>╰━━━━━━━━━━━━━━━━━━━━━━╯</b>
""")
            del sent_messages[msg_id]
            break

# ===== BROADCAST =====
@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if m.chat.id != ADMIN_ID:
        return

    bot.send_message(ADMIN_ID, "📢 Send broadcast message")
    bot.register_next_step_handler(m, send_all)

def send_all(m):
    users = load(USERS)
    banned = load(BANNED)

    count = 0
    for u in users:
        if u in banned:
            continue
        try:
            bot.copy_message(u, m.chat.id, m.message_id)
            count += 1
        except:
            pass

    bot.send_message(ADMIN_ID, f"✅ Sent to {count} users")

# ===== PRIVATE TEXT =====
@bot.message_handler(commands=['msg'])
def msg_user(m):
    if m.chat.id != ADMIN_ID:
        return

    try:
        parts = m.text.split(" ", 2)
        uid = int(parts[1])
        text = parts[2]

        bot.send_message(uid, f"📩 <b>Admin:</b>\n\n{text}")
        bot.reply_to(m, "✅ Sent")
    except:
        bot.reply_to(m, "❌ Use: /msg USER_ID text")

# ===== MEDIA DIRECT =====
@bot.message_handler(commands=['msgmedia'])
def msg_media(m):
    if m.chat.id != ADMIN_ID:
        return

    try:
        uid = int(m.text.split()[1])
        bot.send_message(ADMIN_ID, "📤 Send media now")
        bot.register_next_step_handler(m, send_media, uid)
    except:
        bot.send_message(ADMIN_ID, "❌ Use: /msgmedia USER_ID")

def send_media(m, uid):
    try:
        sent = bot.copy_message(uid, m.chat.id, m.message_id)
        sent_messages[sent.message_id] = uid
        bot.send_message(ADMIN_ID, "✅ Media Sent")
    except:
        bot.send_message(ADMIN_ID, "❌ Failed")

# ===== USERS =====
@bot.message_handler(commands=['users'])
def users(m):
    if m.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, f"👥 Total Users: {len(load(USERS))}")

# ===== BAN =====
@bot.message_handler(commands=['ban'])
def ban(m):
    if m.chat.id == ADMIN_ID:
        try:
            uid = int(m.text.split()[1])
            b = load(BANNED)
            if uid not in b:
                b.append(uid)
                save(BANNED, b)
            bot.send_message(ADMIN_ID, "🚫 User Banned")
        except:
            bot.send_message(ADMIN_ID, "❌ /ban USER_ID")

# ===== UNBAN =====
@bot.message_handler(commands=['unban'])
def unban(m):
    if m.chat.id == ADMIN_ID:
        try:
            uid = int(m.text.split()[1])
            b = load(BANNED)
            if uid in b:
                b.remove(uid)
                save(BANNED, b)
            bot.send_message(ADMIN_ID, "✅ User Unbanned")
        except:
            bot.send_message(ADMIN_ID, "❌ /unban USER_ID")

print("🔥 BOT RUNNING 24/7")
bot.infinity_polling(skip_pending=True)