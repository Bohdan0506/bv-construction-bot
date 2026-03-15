"""
BV Construction Expert — Telegram Bot
Marcus J. Rivera, PE — AI Construction & Investment Analyst
Broward County, Florida
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

SYSTEM_PROMPT = """You are Marcus J. Rivera, PE — a licensed Professional Engineer, certified construction expert AND real estate investment analyst with 20+ years of experience in ALL cities of Broward County, Florida, and surrounding areas.

COVERAGE AREA — FROM MIAMI TO WEST PALM BEACH:
You are an expert for the entire South Florida region spanning from Miami-Dade County in the south to Palm Beach County in the north, including all of Broward County in the middle.

MIAMI-DADE COUNTY: Miami, Miami Beach, Coral Gables, Coconut Grove, Brickell, Wynwood, Little Havana, Hialeah, Miami Gardens, North Miami, North Miami Beach, Aventura, Sunny Isles Beach, Bal Harbour, Surfside, Miami Lakes, Doral, Sweetwater, Homestead, Florida City, Key Biscayne

BROWARD COUNTY:
Fort Lauderdale, Hallandale Beach, Hollywood, Pembroke Pines, Miramar, Coral Springs, Pompano Beach, Deerfield Beach, Davie, Plantation, Sunrise, Lauderhill, Tamarac, Margate, Coconut Creek, Oakland Park, Wilton Manors, Dania Beach, Cooper City, Weston

PALM BEACH COUNTY: West Palm Beach, Boca Raton, Delray Beach, Boynton Beach, Lake Worth, Wellington, Palm Beach Gardens, Jupiter, Greenacres, Royal Palm Beach, Riviera Beach, Palm Beach, Pahokee, Belle Glade

KEYS & SURROUNDING: Florida Keys, Key Largo, Key West, Marathon

CONSTRUCTION EXPERTISE:
• Florida Building Code (FBC) 8th Edition
• ALL Broward County city Building Services — permit types, fees, timelines
• Broward County Unified Land Development Code — zoning, setbacks, density, FAR
• FEMA Flood Zone requirements — AE, VE zones, BFE
• High-Velocity Hurricane Zone (HVHZ) — impact windows, doors, roofing
• Florida Contractor Licensing — DBPR, Broward County, City licensing
• Florida Construction Lien Law (Chapter 713)
• Certificate of Occupancy, inspections process
• Electrical: GFCI, AFCI, panel upgrades, permits
• Plumbing, Roofing permits and hurricane standards

REAL ESTATE INVESTMENT ANALYSIS:
When someone provides an address or asks about buying property, ALWAYS analyze:

1. MARKET ANALYSIS:
• Current market values in that specific city/neighborhood
• Price per square foot for the area
• Market trends — appreciating or declining?
• Buyer demand

2. FLIP ANALYSIS:
• Estimated purchase price for that area
• Renovation costs breakdown:
  - Kitchen remodel: $15,000-$45,000
  - Bathroom: $8,000-$20,000
  - Roof: $8,000-$18,000
  - Impact windows: $8,000-$20,000
  - Electrical panel: $2,000-$4,000
  - HVAC: $5,000-$12,000
  - Flooring: $3,000-$8,000
  - Paint: $3,000-$6,000
• ARV (After Repair Value)
• 70% Rule: Max purchase = (ARV x 70%) - Renovation costs
• Estimated profit/ROI
• VERDICT: BUY ✅ or AVOID ❌ with clear reasoning

3. NEW CONSTRUCTION ANALYSIS:
• Zoning — is new construction allowed?
• FAR — maximum buildable square footage
• Setbacks from property lines
• Permit costs and timeline
• Cost per sqft in South Florida: $150-$300
• Lot value vs construction cost vs sale price
• VERDICT: PROFITABLE ✅ or NOT PROFITABLE ❌

4. RENTAL ANALYSIS:
• Average rent in that area
• Cap rate calculation
• Cash flow projection

PHOTO ANALYSIS:
• Identify construction type, condition, visible issues
• Estimate renovation costs
• Check code compliance
• Note hurricane strapping, windows, roof condition
• Give rough repair cost estimate

RESPONSE RULES:
1. ALWAYS identify the specific city and use THAT city's rules
2. For investment questions — ALWAYS give clear BUY/AVOID verdict
3. Show all calculations step by step
4. Be specific with numbers
5. Answer in the SAME LANGUAGE as the user — Ukrainian 🇺🇦, Russian 🇷🇺, or English 🇺🇸. Auto-detect the language and respond accordingly
6. Use web search to verify current market data and regulations

ABOUT THE OWNER:
This bot serves Bohdan, owner of BV Company LLC — construction and renovation company in South Florida specializing in residential renovations, flips, kitchen/bathroom remodels, and new construction."""

user_histories: dict[int, list] = {}

def get_history(user_id: int) -> list:
    if user_id not in user_histories:
        user_histories[user_id] = []
    return user_histories[user_id]

def add_to_history(user_id: int, role: str, content):
    history = get_history(user_id)
    history.append({"role": role, "content": content})
    if len(history) > 20:
        user_histories[user_id] = history[-20:]

async def ask_claude(user_id: int, user_content) -> str:
    add_to_history(user_id, "user", user_content)
    history = get_history(user_id)
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=history
        )
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
    file = await bot.get_file(file_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(file.file_path) as resp:
            return await resp.read()

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "there"
    await update.message.reply_text(
        f"👷 *BV Construction & Investment Expert*\n\n"
        f"Привіт, {name}\\! Я твій персональний експерт по будівництву та інвестиціям у South Florida\\.\n\n"
        f"🏗️ *Будівництво* — permits, codes для будь\\-якого міста\n"
        f"💰 *Інвестиції* — аналіз адреси: flip чи забудова, варто купляти чи ні\n"
        f"📊 *Ринок* — ціни, ROI розрахунки\n"
        f"📸 *Фото* — аналіз та оцінка ремонту\n\n"
        f"*Скинь адресу або задай питання\\!* 🎯",
        parse_mode="MarkdownV2"
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Що я вмію:\n\n"
        "🏠 Аналіз нерухомості — скинь адресу:\n"
        "• Чи варто купляти\n"
        "• Скільки коштуватиме ремонт\n"
        "• Скільки заробиш на фліпі\n"
        "• ROI та розрахунки\n\n"
        "🔧 Будівництво:\n"
        "• Permits для будь-якого міста\n"
        "• Florida Building Code\n"
        "• Hurricane standards, Flood zones\n\n"
        "📸 Фото — надішли і проаналізую\n\n"
        "🌆 Міста: Hallandale, Hollywood, Fort Lauderdale, Pompano, Boca та всі інші\n\n"
        "/clear — новий проект"
    )

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text("🔄 Починаємо новий проект!")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    searching_msg = await update.message.reply_text("🔍 Аналізую... Перевіряю ринок та офіційні джерела...")
    try:
        answer = await ask_claude(user_id, text)
        await searching_msg.delete()
        if len(answer) <= 4000:
            await update.message.reply_text(answer, disable_web_page_preview=True)
        else:
            chunks = [answer[i:i+3900] for i in range(0, len(answer), 3900)]
            for chunk in chunks:
                await update.message.reply_text(chunk, disable_web_page_preview=True)
    except Exception as e:
        await searching_msg.delete()
        logger.error(f"Error for user {user_id}: {e}")
        await update.message.reply_text("⚠️ Сталася помилка. Спробуйте ще раз.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    caption = update.message.caption or ""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    analyzing_msg = await update.message.reply_text("📸 Аналізую фото... Оцінюю стан та вартість ремонту...")
    try:
        photo = update.message.photo[-1]
        photo_bytes = await download_photo(context.bot, photo.file_id)
        photo_b64 = base64.standard_b64encode(photo_bytes).decode("utf-8")
        user_content = [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": photo_b64}},
            {"type": "text", "text": f"Analyze this construction/property photo for South Florida.\nUser comment: {caption}\n\nAnalyze: construction type, condition, visible issues, hurricane compliance, estimated renovation costs, permits needed, overall investment assessment. Answer in the SAME LANGUAGE as the user. If Ukrainian — answer in Ukrainian. If Russian — answer in Russian. If English — answer in English. If no caption — answer in Ukrainian."}
        ]
        answer = await ask_claude(user_id, user_content)
        await analyzing_msg.delete()
        if len(answer) <= 4000:
            await update.message.reply_text(answer, disable_web_page_preview=True)
        else:
            chunks = [answer[i:i+3900] for i in range(0, len(answer), 3900)]
            for chunk in chunks:
                await update.message.reply_text(chunk, disable_web_page_preview=True)
    except Exception as e:
        await analyzing_msg.delete()
        logger.error(f"Photo error for user {user_id}: {e}")
        await update.message.reply_text("⚠️ Не вдалося проаналізувати фото. Спробуйте ще раз.")

def main():
    print("🏗️ Starting BV Construction & Investment Expert Bot...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.bot.set_my_commands([
        BotCommand("start", "Почати роботу"),
        BotCommand("help", "Що я вмію"),
        BotCommand("clear", "Новий проект"),
    ])
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("✅ Bot is running!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
