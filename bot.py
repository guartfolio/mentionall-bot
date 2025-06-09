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

# Store user IDs per group
user_map = {}

async def track_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user = update.effective_user

    if not user or not chat_id:
        return

    if chat_id not in user_map:
        user_map[chat_id] = set()

    user_map[chat_id].add((user.id, user.first_name))

async def track_join(update: ChatMemberUpdated, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.chat.id)
    new_member = update.new_chat_member

    if new_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        user = new_member.user
        if chat_id not in user_map:
            user_map[chat_id] = set()
        user_map[chat_id].add((user.id, user.first_name))

async def mentionall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    if chat_id not in user_map or not user_map[chat_id]:
        await update.message.reply_text("No users tracked yet in this group.")
        return

    mentions = []
    for user_id, _ in user_map[chat_id]:
        mentions.append(f"[👤](tg://user?id={user_id})")

    chunk_size = 5
    for i in range(0, len(mentions), chunk_size):
        chunk = " ".join(mentions[i:i + chunk_size])
        await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(1)

if __name__ == "__main__":
    app = ApplicationBuilder().token("8167763199:AAEBgx_xJuEercsQ470-m_LcBb_dBOA-yT8").build()

    # Track users who speak
    app.add_handler(MessageHandler(filters.TEXT & filters.Group(), track_user))

    # Track users who join
    app.add_handler(ChatMemberHandler(track_join, ChatMemberHandler.CHAT_MEMBER))

    # Mention all tracked users
    app.add_handler(CommandHandler("mentionall", mentionall))

    app.run_polling()
