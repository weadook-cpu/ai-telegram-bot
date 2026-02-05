import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Получаем токен из переменных среды
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ====== Хэндлеры ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Yapay Zeka Asistanına Hoş Geldin!")

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Вы нажали: {query.data}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Вы написали: {text}")

# ====== Основная функция ======
def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found in environment variables")

    # Создаем приложение
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем хэндлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot aktif 🚀")

    # Запускаем polling
    app.run_polling()

# ====== Запуск бота ======
if __name__ == "__main__":
    main()
