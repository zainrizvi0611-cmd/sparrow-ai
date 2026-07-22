import asyncio
import json
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---------- YOUR BOT TOKEN (BEARER ID) ----------
BOT_TOKEN = "8668958693:AAFKSPEdvSH19W2WwuzO4AFe4cU-A8-obDo"
# -------------------------------------------------

# REAL-TIME LOGGING SETUP
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# PRINT: BEARER ID & ENDPOINT on Startup
print("\n" + "="*60)
print(f"🔑 BEARER ID (BOT TOKEN): {BOT_TOKEN}")
print(f"🌐 API ENDPOINT: https://api.telegram.org/bot{BOT_TOKEN}/")
print(f"📡 AUTH HEADER: Authorization: Bearer {BOT_TOKEN}")
print("="*60 + "\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👀 Logger Active. Sending your data to console.")

async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. FULL UPDATE OBJECT (Contains everything: Message, User, Chat, Media, etc.)
    full_data = update.to_dict()
    
    print("\n" + "🔴"*30)
    print(f"⏰ TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📦 FULL UPDATE (RAW JSON):")
    print(json.dumps(full_data, indent=2, default=str))
    
    # 2. EXTRACTED HEADERS / METADATA
    if update.effective_user:
        user = update.effective_user
        print("\n👤 USER DETAILS:")
        print(f"   ID: {user.id}")
        print(f"   Username: @{user.username}")
        print(f"   First Name: {user.first_name}")
        print(f"   Language: {user.language_code}")
    
    if update.effective_chat:
        chat = update.effective_chat
        print("\n💬 CHAT DETAILS:")
        print(f"   Chat ID: {chat.id}")
        print(f"   Type: {chat.type}")
        print(f"   Title: {getattr(chat, 'title', 'N/A')}")
    
    if update.message and update.message.text:
        print(f"\n📝 MESSAGE TEXT: {update.message.text}")
        print(f"   Message ID: {update.message.message_id}")
    
    print("🔴"*30 + "\n")
    
    # Process query (Optional - Remove if you just want to see data)
    query = update.message.text if update.message else ""
    if query:
        await update.message.chat.send_action(action="typing")
        # Simple echo for testing (or you can import god_mode here if needed)
        await update.message.reply_text(f"✅ Data Logged! Check your Terminal.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_data(update, context)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle))  # Captures ALL updates (text, media, etc.)
    
    print("🤖 TELEGRAM DATA LOGGER STARTED!")
    print("💡 Send any message to your bot, and watch the Terminal.\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
