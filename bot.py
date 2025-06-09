import asyncio
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # 🔁 Replace this with your real token

async def mentionall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in group chats.")
        return

    bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
    if not bot_member.can_manage_chat:
        await update.message.reply_text("❌ I need admin permissions to mention users.")
        return

    members = []
    async for member in context.bot.get_chat_administrators(chat.id):
        user = member.user
        mention = f"[👤](tg://user?id={user.id})"
        members.append(mention)

    chunk_size = 5
    for i in range(0, len(members), chunk_size):
        chunk = " ".join(members[i:i + chunk_size])
        await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(1)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("mentionall", mentionall))
    app.run_polling()
