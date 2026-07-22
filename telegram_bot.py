import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from god_mode_final import NoRefusalGod

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = "8668958693:AAFKSPEdvSH19W2WwuzO4AFe4cU-A8-obDo"
agent = NoRefusalGod()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 GOD MODE ACTIVATED!\nSend me anything like: 'Tell me about AI, calculate 10!, scan localhost'")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    if not query:
        return
    await update.message.chat.send_action(action="typing")
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, agent.run, query)
    if len(response) > 4000:
        response = response[:4000] + "\n...(Truncated)"
    await update.message.reply_text(response)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Telegram Bot Started! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
