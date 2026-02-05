# bot.py - С ГЕНЕРАЦИЕЙ ИЗОБРАЖЕНИЙ
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
    ContextTypes,
    ConversationHandler
)

# Наши модули
from database import Database
from image_generator import image_gen

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

# Инициализация базы данных
db = Database()

# Состояния для ConversationHandler
WAITING_FOR_PROMPT = 1

# Тексты на турецком
TEXTS = {
    "welcome": "👋 Merhaba! Bakiyende {tokens} token var – bunları yapay zeka sorguları için kullanabilirsin.",
    "menu": "👇 Aşağıdaki menüden bir seçenek seçin:",
    "enter_prompt": "🌄 <b>{model}</b> için görsel açıklaması yazın:\n\nÖrnek: 'Gün batımında İstanbul manzarası'",
    "processing": "⏳ Görsel oluşturuluyor... Lütfen bekleyin.",
    "no_tokens": "❌ Yeterli token'ın yok! Gereken: {needed}, Mevcut: {current}",
    "success": "✅ Görsel başarıyla oluşturuldu!\n📸 Harcanan token: {tokens}",
    "error": "❌ Bir hata oluştu. Lütfen tekrar deneyin."
}

# ==================== КЛАВИАТУРЫ ====================
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

def image_generation_menu():
    keyboard = [
        [
            InlineKeyboardButton("🍌 Nano Banana", callback_data="image_nano"),
            InlineKeyboardButton("⭐ Nano Banana Pro", callback_data="image_nano_pro")
        ],
        [
            InlineKeyboardButton("🖼 GPT Image 1.5", callback_data="image_gpt"),
            InlineKeyboardButton("🎨 Midjourney", callback_data="image_midjourney")
        ],
        [
            InlineKeyboardButton("✨ Recraft", callback_data="image_recraft"),
            InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button():
    keyboard = [[InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(keyboard)

def cancel_button():
    keyboard = [[InlineKeyboardButton("❌ İptal", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)

# ==================== ОБРАБОТЧИКИ КОМАНД ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user = update.effective_user
    
    # Получаем реферальный ID
    invited_by = None
    if context.args:
        try:
            invited_by = int(context.args[0])
        except:
            pass
    
    # Добавляем пользователя в базу
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        invited_by=invited_by
    )
    
    # Получаем баланс
    tokens = db.get_user_tokens(user.id)
    
    welcome_text = TEXTS["welcome"].format(tokens=tokens)
    menu_text = TEXTS["menu"]
    
    await update.message.reply_text(
        f"{welcome_text}\n\n{menu_text}",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать баланс"""
    user_id = update.effective_user.id
    tokens = db.get_user_tokens(user_id)
    
    await update.message.reply_text(
        f"💰 <b>Bakiye:</b> {tokens:,} token\n\n"
        "Token paketleri yakında gelecek!",
        reply_markup=back_button(),
        parse_mode="HTML"
    )

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать историю"""
    user_id = update.effective_user.id
    history = db.get_user_history(user_id)
    
    if not history:
        await update.message.reply_text(
            "📭 Henüz işlem geçmişiniz yok.",
            reply_markup=back_button()
        )
        return
    
    text = "📊 <b>Son İşlemleriniz:</b>\n\n"
    for item in history[:5]:
        action = item['action']
        tokens = item['tokens_change']
        details = item['details'][:30] if item['details'] else ""
        date = item['timestamp'][:16]
        
        text += f"• {action}\n"
        text += f"  🪙 {tokens:+d} token\n"
        if details:
            text += f"  📝 {details}...\n"
        text += f"  🕐 {date}\n\n"
    
    await update.message.reply_text(
        text,
        reply_markup=back_button(),
        parse_mode="HTML"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    help_text = """
🤖 <b>AI Bot - Yardım</b>

<b>Nasıl Kullanılır:</b>
1. Menüden bir araç seçin
2. İsteğinizi yazın (görsel açıklaması, soru vb.)
3. Token'larınızla ödeme yapın
4. Sonucu alın!

<b>Token Sistemi:</b>
• Yeni kullanıcı: 15.000 token
• Görsel oluşturma: 100-300 token
• Dil modelleri: 5-20 token/soru

<b>API Durumu:</b>
• Gemini API: {'✅ Aktif' if image_gen.validate_api_key() else '❌ Pasif'}
• Demo Modu: {'✅ Aktif'}

<b>Destek:</b>
Sorularınız için iletişime geçin.
    """
    
    await update.message.reply_text(
        help_text,
        reply_markup=back_button(),
        parse_mode="HTML"
    )

# ==================== ОБРАБОТЧИКИ КНОПОК ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    # Главное меню
    if data == "back_to_main":
        tokens = db.get_user_tokens(user_id)
        welcome_text = TEXTS["welcome"].format(tokens=tokens)
        
        await query.edit_message_text(
            text=f"{welcome_text}\n\n{TEXTS['menu']}",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    
    elif data == "menu_llm":
        await query.edit_message_text(
            text="💬 <b>Dil Modelleri</b>\n\nYakında eklenecek!",
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "menu_image":
        await query.edit_message_text(
            text="🌄 <b>Fotoğraf Oluşturma Araçları</b>\n\nHangi aracı kullanmak istiyorsunuz?",
            reply_markup=image_generation_menu(),
            parse_mode="HTML"
        )
    
    elif data == "menu_video":
        await query.edit_message_text(
            text="📹 <b>Video Oluşturma</b>\n\nYakında eklenecek!",
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "menu_audio":
        await query.edit_message_text(
            text="🎙 <b>Ses Araçları</b>\n\nYakında eklenecek!",
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "balance":
        tokens = db.get_user_tokens(user_id)
        await query.edit_message_text(
            text=f"💰 <b>Bakiye:</b> {tokens:,} token\n\n"
                 "Token paketleri yakında gelecek!",
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "history":
        await history_callback(query, user_id)
    
    elif data == "invite":
        bot_username = (await context.bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        
        await query.edit_message_text(
            text=f"🎁 <b>Arkadaşını Davet Et</b>\n\n"
                 f"Davet Linkin:\n<code>{ref_link}</code>\n\n"
                 f"Her davet için: 2.000 token\n"
                 f"Davet ettiğin kişiler: 0",
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "help":
        await help_callback(query)
    
    elif data == "cancel":
        await query.edit_message_text(
            text="❌ İşlem iptal edildi.",
            reply_markup=back_button()
        )
    
    # Выбор модели генерации изображений
    elif data.startswith("image_"):
        await handle_image_model_selection(query, user_id, data)
    
    # Языковые модели
    elif data.startswith("model_"):
        await query.edit_message_text(
            text="💬 <b>Dil Modelleri</b>\n\nYakında eklenecek!",
            reply_markup=back_button(),
            parse_mode="HTML"
        )

async def handle_image_model_selection(query, user_id, data):
    """Обработка выбора модели генерации"""
    model_map = {
        "image_nano": ("🍌 Nano Banana", "nano", 100),
        "image_nano_pro": ("⭐ Nano Banana Pro", "nano_pro", 200),
        "image_gpt": ("🖼 GPT Image 1.5", "gpt", 150),
        "image_midjourney": ("🎨 Midjourney", "midjourney", 300),
        "image_recraft": ("✨ Recraft", "recraft", 250)
    }
    
    if data not in model_map:
        await query.edit_message_text(
            text="❌ Geçersiz seçim.",
            reply_markup=back_button()
        )
        return
    
    model_name, model_key, price = model_map[data]
    
    # Проверяем баланс
    user_tokens = db.get_user_tokens(user_id)
    
    if user_tokens < price:
        await query.edit_message_text(
            text=TEXTS["no_tokens"].format(needed=price, current=user_tokens),
            reply_markup=back_button()
        )
        return
    
    # Сохраняем выбранную модель в контекст
    query.message.model_key = model_key
    query.message.model_name = model_name
    query.message.price = price
    
    await query.edit_message_text(
        text=TEXTS["enter_prompt"].format(model=model_name),
        reply_markup=cancel_button(),
        parse_mode="HTML"
    )
    
    return WAITING_FOR_PROMPT

# ==================== ОБРАБОТКА ПРОМПТОВ ====================
async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстового промпта для генерации"""
    user_id = update.effective_user.id
    prompt = update.message.text
    
    # Получаем сохранённые данные из контекста
    # (в реальности нужно хранить в context.user_data)
    
    # Для демо используем Nano Banana модель
    model_key = "nano"
    model_name = "🍌 Nano Banana"
    price = 100
    
    # Проверяем баланс
    user_tokens = db.get_user_tokens(user_id)
    if user_tokens < price:
        await update.message.reply_text(
            TEXTS["no_tokens"].format(needed=price, current=user_tokens),
            reply_markup=back_button()
        )
        return
    
    # Сообщение о начале генерации
    processing_msg = await update.message.reply_text(
        TEXTS["processing"],
        reply_markup=None
    )
    
    try:
        # Генерируем изображение
        image_url, tokens_spent, error = image_gen.generate_image(
            prompt=prompt,
            model_type=model_key
        )
        
        if error and "demo" not in error.lower():
            await processing_msg.edit_text(
                f"❌ Hata: {error}",
                reply_markup=back_button()
            )
            return
        
        # Списание токенов
        db.add_tokens(user_id, -tokens_spent, "image_generation", 
                     f"{model_name}: {prompt[:50]}")
        
        # Добавляем запись в базу
        db.add_image_record(user_id, model_name, prompt, image_url, tokens_spent)
        
        # Отправляем изображение
        await update.message.reply_photo(
            photo=image_url,
            caption=f"🎨 <b>{model_name}</b>\n\n"
                   f"📝 <b>Prompt:</b> {prompt}\n"
                   f"🪙 <b>Token:</b> {tokens_spent}\n"
                   f"💰 <b>Kalan bakiye:</b> {db.get_user_tokens(user_id)}",
            parse_mode="HTML",
            reply_markup=back_button()
        )
        
        # Удаляем сообщение "обработка"
        await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        await processing_msg.edit_text(
            f"❌ Bir hata oluştu: {str(e)}",
            reply_markup=back_button()
        )

async def history_callback(query, user_id):
    """Callback для истории"""
    history = db.get_user_history(user_id)
    
    if not history:
        await query.edit_message_text(
            "📭 Henüz işlem geçmişiniz yok.",
            reply_markup=back_button()
        )
        return
    
    text = "📊 <b>Son İşlemleriniz:</b>\n\n"
    for item in history[:5]:
        action = item['action']
        tokens = item['tokens_change']
        details = item['details'][:30] if item['details'] else ""
        date = item['timestamp'][:16]
        
        text += f"• {action}\n"
        text += f"  🪙 {tokens:+d} token\n"
        if details:
            text += f"  📝 {details}...\n"
        text += f"  🕐 {date}\n\n"
    
    await query.edit_message_text(
        text,
        reply_markup=back_button(),
        parse_mode="HTML"
    )

async def help_callback(query):
    """Callback для помощи"""
    help_text = """
🤖 <b>AI Bot - Yardım</b>

<b>Görsel Oluşturma:</b>
1. "Fotoğraf Oluştur" butonuna tıklayın
2. Bir model seçin
3. Görsel açıklaması yazın
4. Token'larınızla ödeme yapın
5. Görselinizi alın!

<b>Token:</b>
• Yeni kullanıcı: 15.000 ücretsiz token
• Görsel başına: 100-300 token
• Bakiye: /balance komutu

<b>Demo Modu:</b>
Şu anda demo modunda çalışıyor. 
Gerçek API bağlantısı için ayarlar yapılacak.
    """
    
    await query.edit_message_text(
        help_text,
        reply_markup=back_button(),
        parse_mode="HTML"
    )

# ==================== ЗАПУСК БОТА ====================
def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN bulunamadı!")
        return
    
    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчики текстовых сообщений
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_prompt
    ))
    
    # Запуск
    logger.info("✅ 🤖 AI Telegram Bot başlatılıyor...")
    logger.info(f"✅ Gemini API durumu: {image_gen.validate_api_key()}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
