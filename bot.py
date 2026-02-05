import os
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ====== НАСТРОЙКИ ======

BOT_TOKEN = os.getenv("BOT_TOKEN")

START_BALANCE = 15000


# ====== КНОПКИ ======

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Metin", callback_data="text")],
        [InlineKeyboardButton("🖼 Görsel", callback_data="image")],
        [InlineKeyboardButton("🎬 Video", callback_data="video")],
        [InlineKeyboardButton("🎧 Ses", callback_data="audio")],
        [InlineKeyboardButton("💎 Bakiye", callback_data="balance")],
        [InlineKeyboardButton("💳 Paket Al", callback_data="buy")]
    ])


# ====== ПАМЯТЬ (ВРЕМЕННО) ======
# Потом заменим на базу данных

users = {}


# ====== START ======

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = START_BALANCE

    text = """
🤖 Yapay Zeka Asistanına Hoş Geldin!

💎 15.000 Ücretsiz Token
⚡ Hızlı & Kolay
🔥 Metin • Görsel • Video • Ses

Ne yapmak istiyorsun?
"""

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard()
    )


# ====== КНОПКИ ======

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    data = q.data

    if user_id not in users:
        users[user_id] = START_BALANCE

    if data == "text":
        context.user_data["mode"] = "text"
        await q.message.reply_text("✍️ Metnini yaz:")

    elif data == "image":
        context.user_data["mode"] = "image"
        await q.message.reply_text("🖼 Görsel açıklamasını yaz:")

    elif data == "video":
        context.user_data["mode"] = "video"
        await q.message.reply_text("🎬 Video açıklamasını yaz:")

    elif data == "audio":
        context.user_data["mode"] = "audio"
        await q.message.reply_text("🎧 Ses için metin yaz:")

    elif data == "balance":
        bal = users.get(user_id, 0)
        await q.message.reply_text(f"💎 Bakiyen: {bal} Token")

    elif data == "buy":

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Starter ₺49", url="https://example.com/pay1")],
            [InlineKeyboardButton("🔥 Pro ₺119", url="https://example.com/pay2")],
            [InlineKeyboardButton("👑 Ultra ₺299", url="https://example.com/pay3")]
        ])

        await q.message.reply_text(
            "💳 Paket seç:",
            reply_markup=keyboard
        )


# ====== ОБРАБОТКА ТЕКСТА ======

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    mode = context.user_data.get("mode")

    if user_id not in users:
        users[user_id] = START_BALANCE

    if not mode:
        await update.message.reply_text("Önce bir mod seç 👇")
        return

    if users[user_id] <= 0:
        await update.message.reply_text("⚠️ Tokenlerin bitti! Paket al 💳")
        return

    prompt = update.message.text

    users[user_id] -= 50  # списание токенов

    await update.message.reply_text("⏳ İşleniyor...")

    # === ВРЕМЕННО: заглушка ===
    result = f"✅ ({mode.upper()}) Sonuç:\n\n{prompt}"

    await update.message.reply_text(result)


# ====== ЗАПУСК ======

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))

    print("Bot aktif 🚀")

    app.run_polling()


if __name__ == "__main__":
    main()
