import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8936047887:AAGgvjEL4tvxAVV0Wl3V3IqvzmENWB2q78A"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Ready. Send anything.")

async def log_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("\n" + "="*80)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📦 FULL UPDATE (JSON):")
    print(json.dumps(update.to_dict(), indent=2, default=str))
    print("="*80 + "\n")
    await update.message.reply_text("✅ Data logged!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, log_all))
    print("🤖 BOT RUNNING... Check Telegram")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
