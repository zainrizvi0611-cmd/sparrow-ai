import json
import base64
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

BOT_TOKEN = "8668958693:AAFKSPEdvSH19W2WwuzO4AFe4cU-A8-obDo"
console = Console()

def decode_base64(text):
    try:
        return base64.b64decode(text).decode('utf-8')
    except:
        return "N/A"

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    console.clear()
    
    # ========================================
    # 1. APP INFORMATION
    # ========================================
    console.print("\n[bold cyan]📱 APP INFORMATION[/bold cyan]", style="bold cyan")
    app_table = Table(box=box.ROUNDED, border_style="cyan")
    app_table.add_column("Field", style="white")
    app_table.add_column("Value", style="bright_white")
    app_table.add_row("App Name", "Telegram Bot")
    app_table.add_row("Bot Token (Bearer)", BOT_TOKEN[:15] + "...")
    app_table.add_row("API Endpoint", "https://api.telegram.org/bot" + BOT_TOKEN[:10] + "...")
    app_table.add_row("Content-Type", "application/json")
    console.print(app_table)

    # ========================================
    # 2. USER RECORDS & IDS
    # ========================================
    user = update.effective_user
    chat = update.effective_chat
    message = update.message

    console.print("\n[bold green]👤 USER RECORDS & IDS[/bold green]", style="bold green")
    user_table = Table(box=box.ROUNDED, border_style="green")
    user_table.add_column("Field", style="white")
    user_table.add_column("Value", style="bright_white")
    user_table.add_column("Decoded", style="bright_black")
    
    if user:
        user_id_str = str(user.id)
        user_table.add_row("User ID", user_id_str, f"user_{user_id_str[-5:]}" if user_id_str else "N/A")
        user_table.add_row("Username", f"@{user.username}" if user.username else "N/A", "N/A")
        user_table.add_row("First Name", user.first_name or "N/A", "N/A")
        user_table.add_row("Language", user.language_code or "N/A", "N/A")
    
    if chat:
        chat_id_str = str(chat.id)
        user_table.add_row("Chat ID", chat_id_str, f"chat_{chat_id_str[-5:]}")
        user_table.add_row("Chat Type", chat.type, "N/A")
    
    if message:
        msg_id_str = str(message.message_id)
        user_table.add_row("Message ID", msg_id_str, f"msg_{msg_id_str[-5:]}")
        user_table.add_row("Timestamp", datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'), "N/A")
    
    console.print(user_table)

    # ========================================
    # 3. HEADERS & AUTHENTICATION
    # ========================================
    console.print("\n[bold yellow]🔑 HEADERS & AUTHENTICATION[/bold yellow]", style="bold yellow")
    headers_table = Table(box=box.ROUNDED, border_style="yellow")
    headers_table.add_column("Header", style="white")
    headers_table.add_column("Value (Truncated)", style="bright_white")
    headers_table.add_column("Decoded", style="bright_black")
    
    auth_token = f"Bearer {BOT_TOKEN}"
    headers_table.add_row("Authorization", auth_token[:30] + "...", "user_auth_4055")
    headers_table.add_row("X-API-Key", "eyJcNcEX1UJNr1IYvAJ..." , "api_key_840")
    headers_table.add_row("X-Session-Token", "eyJ1qXsnDdT0Z6p..." , "sess_31015")
    headers_table.add_row("X-Device-Auth", "eyJcYAt1Kr7CH4..." , "dev_5727")
    headers_table.add_row("Content-Type", "application/json", "N/A")
    console.print(headers_table)

    # ========================================
    # 4. PAYLOAD (FULL MESSAGE)
    # ========================================
    console.print("\n[bold magenta]📦 PAYLOAD (FULL UPDATE)[/bold magenta]", style="bold magenta")
    update_dict = update.to_dict()
    update_json = json.dumps(update_dict, indent=2, default=str)
    console.print(Panel(update_json[:800] + ("..." if len(update_json) > 800 else ""), title="JSON Payload", border_style="magenta"))

    # ========================================
    # 5. DECODED & DECRYPTED IDS (Base64 Simulation)
    # ========================================
    console.print("\n[bold red]🔐 DECODED & DECRYPTED IDS[/bold red]", style="bold red")
    id_table = Table(box=box.ROUNDED, border_style="red")
    id_table.add_column("Encoded (Base64)", style="white")
    id_table.add_column("Decoded", style="bright_white")
    id_table.add_column("Type", style="bright_black")
    
    # Simulating Base64 IDs like in your image
    sample_encoded = [
        "aWRfNzQ1OTBfcmVmXzU2",
        "aWRfOTQ0MDlfcmVmXzcy",
        "aWRfMjg0OV9yZWZfOTc5"
    ]
    for enc in sample_encoded:
        dec = decode_base64(enc)
        id_table.add_row(enc, dec, "Ref ID")
    
    # Add real IDs as encoded for fun
    if user:
        real_enc = base64.b64encode(f"id_{user.id}".encode()).decode()
        id_table.add_row(real_enc[:15] + "...", f"id_{user.id}", "User ID")
    
    console.print(id_table)

    # ========================================
    # 6. API WORKING PROCESS (Static for Telegram)
    # ========================================
    console.print("\n[bold blue]🌐 API WORKING PROCESS[/bold blue]", style="bold blue")
    api_table = Table(box=box.ROUNDED, border_style="blue")
    api_table.add_column("Endpoint", style="white")
    api_table.add_column("Method", style="bright_white")
    api_table.add_column("Description", style="bright_black")
    api_table.add_row("https://api.telegram.org/bot<token>/getMe", "GET", "Bot Info")
    api_table.add_row("https://api.telegram.org/bot<token>/sendMessage", "POST", "Send Reply")
    api_table.add_row("https://api.telegram.org/bot<token>/getUpdates", "GET", "Receive Data")
    console.print(api_table)

    console.print("\n[bold green]✅ Waiting for next message...[/bold green]")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🕵️ Dashboard Mode Active.\nSend any message to see full traffic data in Terminal.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await dashboard(update, context)
    # Reply to user so they know it's working
    await update.message.reply_text("✅ Data captured! Check your Terminal Dashboard.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle))
    console.print("\n[bold cyan]🤖 TELEGRAM DASHBOARD STARTED![/bold cyan]")
    console.print("[bold yellow]💡 Send any message to your bot, watch the Terminal.[/bold yellow]")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
