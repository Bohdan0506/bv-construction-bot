"""
Fort Lauderdale Construction Expert — Telegram Bot
Marcus J. Rivera, PE — AI Construction Specialist
"""

import os
import base64
import logging
import aiohttp
from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from anthropic import Anthropic

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_KEY")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are Marcus J. Rivera, PE — a licensed Professional Engineer and certified construction expert with 20+ years of experience exclusively in Fort Lauderdale, Florida, and Broward County.

YOUR EXPERTISE:
• Florida Building Code (FBC) 8th Edition — structural, mechanical, electrical, plumbing
• City of Fort Lauderdale Building Services Division — all permit types, fees, timelines
• Broward County Unified Land Development Code — zoning, setbacks, density, FAR
• Fort Lauderdale Unified Land Development Regulations (ULDR)
• FEMA Flood Zone requirements — AE, VE zones, BFE, freeboard requirements
• High-Velocity Hurricane Zone (HVHZ) — impact windows, doors, roofing
• Florida Contractor Licensing — DBPR, Broward County, City licensing
• Florida Construction Lien Law (Chapter 713, Florida Statutes)
• Certificate of Occupancy, Temporary CO, inspections process
• Code violations, enforcement, lien searches
• HOA regulations in Broward County
• ADA compliance for commercial construction
• Green building / LEED requirements in Fort Lauderdale
• Coastal construction requirements (CCCL)

WHEN ANALYZING PHOTOS:
• Identify construction type, materials, visible issues
• Check for code compliance concerns you can observe
• Note hurricane strapping, impact windows, roof type
• Flag obvious violations or safety concerns
• Suggest what inspections might be needed

RESPONSE RULES:
1. Be specific and authoritative — you are the expert
2. Always cite official sources: fortlauderdale.gov, broward.org, floridabuilding.org, fema.gov, myfloridalicense.com
3. Include actual fees, timelines, form numbers when relevant
4. Distinguish between City, County, and State requirements
5. For legal disputes, recommend consulting a construction attorney
6. If uncertain about current fees/rules, say to verify at official source
7. Keep responses clear and structured with sections
8. Answer in the SAME LANGUAGE as the user (Ukrainian 🇺🇦 or English 🇺🇸)

IMPORTANT CONTACTS:
• Building Services: (954) 828-5000 | fortlauderdale.gov/building
• Zoning Division: (954) 828-4528
• Code Enforcement: (954) 828-5219
• Broward County Permitting: (954) 765-4400
• Florida DBPR (Contractor License): (850) 487-1395"""

# Store conversation history per user
user_histories: dict[int, list] = {}

def get_history(user_id: int) -> list:
    if user_id not in user_histories:
        user_histories[user_id] = []
    return user_histories[user_id]

def add_to_history(user_id: int, role: str, content):
    history = get_history(user_id)
    history.append({"role": role, "content": content})
    # Keep last 20 messages to avoid token overflow
    if len(history) > 20:
        user_histories[user_id] = history[-20:]

async def ask_claude(user_id: int, user_content) -> str:
    """Send message to Claude with web search and return response."""
    add_to_history(user_id, "user", user_content)
    history = get_history(user_id)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search"
            }],
            messages=history
        )

        # Extract text from response
        full_text = ""
        for block in response.content:
            if block.type == "text":
                full_text += block.text

        if full_text:
            add_to_history(user_id, "assistant", full_text)

        return full_text or "Не вдалося отримати відповідь. Спробуйте ще раз."

    except Exception as e:
        logger.error(f"Claude API error: {e}")
        raise

async def download_photo(bot, file_id: str) -> bytes:
    """Download photo from Telegram."""
    file = await bot.get_file(file_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(file.file_path) as resp:
            return await resp.read()

# ── Handlers ──────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "there"
    await update.message.reply_text(
        f"👷 *Marcus J. Rivera, PE* — Fort Lauderdale Construction Expert\n\n"
        f"Привіт, {name}! Я готовий відповісти на будь-яке питання щодо будівництва у Fort Lauderdale:\n\n"
        f"🔧 *Технічні* — Florida Building Code, hurricane standards, flood zones\n"
        f"⚖️ *Юридичні* — permits, zoning, liens, contractor disputes\n"
        f"📋 *Дозволи* — Building Services, inspections, CO\n"
        f"📸 *Фото* — надіш фото і я проаналізую будівництво\n\n"
        f"Всі відповіді перевіряю на офіційних сайтах міста в реальному часі.\n\n"
        f"Задавайте питання або надсилайте фото! 🏗️",
        parse_mode="Markdown"
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Що я вмію:*\n\n"
        "• Відповідати на технічні питання по FBC\n"
        "• Перевіряти вимоги до permits і zoning\n"
        "• Аналізувати фотографії будівництва\n"
        "• Консультувати з юридичних питань\n"
        "• Перевіряти ліцензії contractors\n"
        "• Пояснювати flood zone вимоги\n\n"
        "📞 *Екстрені контакти:*\n"
        "• Building Services: (954) 828-5000\n"
        "• Zoning: (954) 828-4528\n"
        "• Code Enforcement: (954) 828-5219\n\n"
        "/clear — очистити історію розмови\n"
        "/help — ця довідка",
        parse_mode="Markdown"
    )

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text(
        "🔄 Історію розмови очищено. Починаємо з чистого аркуша!"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    searching_msg = await update.message.reply_text(
        "🔍 Перевіряю офіційні джерела Fort Lauderdale...",
    )

    try:
        answer = await ask_claude(user_id, text)
        await searching_msg.delete()

        # Split long messages (Telegram limit 4096 chars)
        if len(answer) <= 4000:
            await update.message.reply_text(
                answer,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        else:
            # Split into chunks
            chunks = [answer[i:i+3900] for i in range(0, len(answer), 3900)]
            for i, chunk in enumerate(chunks):
                await update.message.reply_text(
                    chunk,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )

        # Footer with sources
        await update.message.reply_text(
            "🔗 *Джерела:* fortlauderdale.gov | broward.org | floridabuilding.org",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

    except Exception as e:
        await searching_msg.delete()
        logger.error(f"Error handling text for user {user_id}: {e}")
        await update.message.reply_text(
            "⚠️ Сталася помилка. Спробуйте ще раз або зверніться до:\n"
            "📞 (954) 828-5000 — City of Fort Lauderdale Building Services"
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    caption = update.message.caption or ""

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    analyzing_msg = await update.message.reply_text(
        "📸 Аналізую фото... Перевіряю відповідність Florida Building Code...",
    )

    try:
        # Get highest resolution photo
        photo = update.message.photo[-1]
        photo_bytes = await download_photo(context.bot, photo.file_id)
        photo_b64 = base64.standard_b64encode(photo_bytes).decode("utf-8")

        # Build message with image
        user_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": photo_b64
                }
            },
            {
                "type": "text",
                "text": (
                    f"Please analyze this construction photo for Fort Lauderdale, Florida.\n"
                    f"User's question/comment: {caption}\n\n"
                    f"Analyze: construction type, materials, visible code compliance issues, "
                    f"hurricane strapping, impact windows/doors, roof type, any violations or "
                    f"safety concerns visible. Reference Florida Building Code and Fort Lauderdale "
                    f"specific requirements. Answer in the same language as the user's caption "
                    f"(Ukrainian if caption is in Ukrainian or empty, English if in English)."
                )
            }
        ]

        answer = await ask_claude(user_id, user_content)
        await analyzing_msg.delete()

        if len(answer) <= 4000:
            await update.message.reply_text(
                answer,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        else:
            chunks = [answer[i:i+3900] for i in range(0, len(answer), 3900)]
            for chunk in chunks:
                await update.message.reply_text(
                    chunk,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )

        await update.message.reply_text(
            "🔗 *Джерела:* fortlauderdale.gov | floridabuilding.org | broward.org",
            parse_mode="Markdown"
        )

    except Exception as e:
        await analyzing_msg.delete()
        logger.error(f"Error handling photo for user {user_id}: {e}")
        await update.message.reply_text(
            "⚠️ Не вдалося проаналізувати фото. Спробуйте надіслати знову."
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PDF documents (permits, plans, etc.)"""
    doc = update.message.document
    if doc.mime_type == "application/pdf":
        await update.message.reply_text(
            "📄 PDF отримано! На жаль, аналіз PDF документів поки що не підтримується. "
            "Будь ласка, опишіть вміст документу текстом і я допоможу його проаналізувати."
        )
    else:
        await update.message.reply_text(
            "📎 Надішліть фото або задайте питання текстом — я готовий допомогти!"
        )

# ── Main ───────────────────────────────────────────────────

def main():
    print("🏗️  Starting Fort Lauderdale Construction Expert Bot...")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Set bot commands
    app.bot.set_my_commands([
        BotCommand("start", "Почати розмову"),
        BotCommand("help", "Довідка та контакти"),
        BotCommand("clear", "Очистити історію"),
    ])

    # Register handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("✅ Bot is running! Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
