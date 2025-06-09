import asyncio
import json
import os
from telegram import Update, ChatMemberUpdated
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ChatMemberHandler, filters, ContextTypes
)

BOT_TOKEN = os.getenv("8167763199:AAEBgx_xJuEercsQ470-m_LcBb_dBOA-yT8") or "8167763199:AAEBgx_xJuEercsQ470-m_LcBb_dBOA-yT8"
DATA_FILE = "users.json"

# Load users.json if it exists
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        user_map = json.load(f)
        user_map = {
            group_id: set(tuple(user) for user in users)
            for group_id, users in user_map.items()
        }
else:
    user_map = {}

# Save users to file
def save_user_data():
    serializable_map = {
        group_id: list(users)
        for group_id, users in user_map.items()
    }
    with open(DATA_FILE, "w") as f:
        json.dump(serializable_map, f)

async def track_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user = update.effective_user
    if not user or not chat_id:
        return
    if chat_id not in user_map:
        user_map[chat_id] = set()
    user_map[chat_id].add((user.id, user.first_name))
    save_user_data()

async def track_join(update: ChatMemberUpdated, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.chat.id)
    new_member = update.new_chat_member
    if new_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        user = new_member.user
        if chat_id not in user_map:
            user_map[chat_id] = set()
        user_map[chat_id].add((user.id, user.first_name))
        save_user_data()

async def mention_users(chat_id, context):
    mentions = []
    for user_id, _ in user_map.get(chat_id, set()):
        mentions.append(f"[👤](tg://user?id={user_id})")
    chunk_size = 5
    for i in range(0, len(mentions), chunk_size):
        chunk = " ".join(mentions[i:i + chunk_size])
        await context.bot.send_message(chat_id=chat_id, text=chunk, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(1)

async def mentionall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if chat_id not in user_map or not user_map[chat_id]:
        await update.message.reply_text("No users tracked yet in this group.")
        return
    await mention_users(chat_id, context)

async def forceupdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if chat_id not in user_map:
        user_map[chat_id] = set()

    admins = await context.bot.get_chat_administrators(chat_id)
    for admin in admins:
        user = admin.user
        user_map[chat_id].add((user.id, user.first_name))

    save_user_data()

    await update.message.reply_text(
        "Force update triggered! If you'd like to be included in group mentions, type anything in the chat."
    )

    await mention_users(chat_id, context)

if __name__ == "__main__":
    app = ApplicationBuilder().token("8167763199:AAEBgx_xJuEercsQ470-m_LcBb_dBOA-yT8").build()

    # ✅ Fixed filter syntax for PTB v20+
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, track_user))
    app.add_handler(ChatMemberHandler(track_join, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CommandHandler("mentionall", mentionall))
    app.add_handler(CommandHandler("forceupdate", forceupdate))

    app.run_polling()
