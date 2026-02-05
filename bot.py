# bot.py - БЕЗ БАЗЫ ДАННЫХ (для начала)
import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Тексты на турецком
TEXTS = {
    "welcome": "👋 Merhaba! Bakiyende {tokens} token var – bunları yapay zeka sorguları için kullanabilirsin.",
    "menu": "👇 Aşağıdaki menüden bir seçenek seçin:"
}

# Клавиатуры
def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("💬 Dil Modelleri", callback_data="menu_llm"),
            InlineKeyboardButton("🌄 Fotoğraf Oluştur", callback_data="menu_image")
        ],
        [
            InlineKeyboardButton("📹 Video Oluştur", callback_data="menu_video"),
            InlineKeyboardButton("🎙 Ses Araçları", callback_data="menu_audio")
        ],
        [
            InlineKeyboardButton("💰 Bakiye", callback_data="balance"),
            InlineKeyboardButton("📊 Geçmişim", callback_data="history")
        ],
        [
            InlineKeyboardButton("🎁 Arkadaşını Davet Et", callback_data="invite"),
            InlineKeyboardButton("ℹ️ Yardım", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button():
    keyboard = [[InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(keyboard)

# Обработчики команд
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user = update.effective_user
    
    welcome_text = TEXTS["welcome"].format(tokens=15000)
    menu_text = TEXTS["menu"]
    
    await update.message.reply_text(
        f"{welcome_text}\n\n{menu_text}",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать баланс"""
    await update.message.reply_text(
        "💰 <b>Bakiye:</b> 15.000 token\n\n"
        "Token paketleri yakında gelecek!",
        reply_markup=back_button(),
        parse_mode="HTML"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_main":
        welcome_text = TEXTS["welcome"].format(tokens=15000)
        await query.edit_message_text(
            text=f"{welcome_text}\n\n{TEXTS['menu']}",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    
    elif data == "menu_llm":
        keyboard = [
            [InlineKeyboardButton("ChatGPT", callback_data="model_chatgpt"),
             InlineKeyboardButton("Gemini", callback_data="model_gemini")],
            [InlineKeyboardButton("Claude", callback_data="model_claude"),
             InlineKeyboardButton("DeepSeek", callback_data="model_deepseek")],
            [InlineKeyboardButton("Grok", callback_data="model_grok"),
             InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(
            text="💬 <b>Dil Modelleri</b>\n\nHangi modeli kullanmak istiyorsunuz?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    
    elif data == "menu_image":
        keyboard = [
            [InlineKeyboardButton("🍌 Nano Banana", callback_data="image_nano"),
             InlineKeyboardButton("⭐ Nano Banana Pro", callback_data="image_nano_pro")],
            [InlineKeyboardButton("🖼 GPT Image 1.5", callback_data="image_gpt"),
             InlineKeyboardButton("🎨 Midjourney", callback_data="image_midjourney")],
            [InlineKeyboardButton("✨ Recraft", callback_data="image_recraft"),
             InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(
            text="🌄 <b>Fotoğraf Oluşturma Araçları</b>\n\nHangi aracı kullanmak istiyorsunuz?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    
    elif data == "balance":
        await query.edit_message_text(
            text="💰 <b>Bakiye:</b> 15.000 token\n\n"
                 "Token paketleri yakında gelecek!",
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data.startswith("model_"):
        model_name = data.replace("model_", "")
        models = {
            "chatgpt": "ChatGPT",
            "gemini": "Google Gemini", 
            "claude": "Anthropic Claude",
            "deepseek": "DeepSeek",
            "grok": "Grok"
        }
        
        model_display = models.get(model_name, model_name)
        
        await query.edit_message_text(
            text=f"💬 <b>{model_display}</b>\n\n"
                 "Bu özellik şu anda geliştirme aşamasındadır.\n"
                 "Yakında kullanıma açılacak!",
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data.startswith("image_"):
        model_name = data.replace("image_", "")
        models = {
            "nano": "🍌 Nano Banana",
            "nano_pro": "⭐ Nano Banana Pro",
            "gpt": "🖼 GPT Image 1.5",
            "midjourney": "🎨 Midjourney",
            "recraft": "✨ Recraft"
        }
        
        model_display = models.get(model_name, model_name)
        
        await query.edit_message_text(
            text=f"🌄 <b>{model_display}</b>\n\n"
                 "Bu özellik şu anda geliştirme aşamasındadır.\n"
                 "Yakında kullanıma açılacak!",
            reply_markup=back_button(),
            parse_mode="HTML"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    await update.message.reply_text(
        "🤖 <b>Yardım</b>\n\n"
        "Bu bot yapay zeka araçlarını kullanmanızı sağlar.\n"
        "Her yeni kullanıcı 15.000 ücretsiz token alır.\n\n"
        "Geliştirme aşamasındadır. Yakında daha fazla özellik!",
        reply_markup=back_button(),
        parse_mode="HTML"
    )

# Основная функция
def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запуск бота
    logger.info("🤖 AI Telegram Bot başlatılıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
