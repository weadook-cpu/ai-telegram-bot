# bot.py - УПРОЩЕННАЯ ВЕРСИЯ С NANO BANANA
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

# ==================== КЛАВИАТУРЫ ====================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🌄 Fotoğraf Oluştur", callback_data="menu_image")],
        [InlineKeyboardButton("💬 Dil Modelleri", callback_data="menu_llm")],
        [InlineKeyboardButton("💰 Bakiye", callback_data="balance")],
        [InlineKeyboardButton("📊 Geçmişim", callback_data="history")],
        [InlineKeyboardButton("🎁 Davet Et", callback_data="invite")],
        [InlineKeyboardButton("ℹ️ Yardım", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def image_generation_menu():
    keyboard = [
        [InlineKeyboardButton("🍌 Nano Banana - Görsel Oluştur", callback_data="image_nano")],
        [InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
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
    
    welcome_text = f"👋 Merhaba {user.first_name}! Bakiyende {tokens:,} token var"
    
    await update.message.reply_text(
        f"{welcome_text}\n\n👇 Aşağıdaki menüden bir seçenek seçin:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать баланс"""
    user_id = update.effective_user.id
    tokens = db.get_user_tokens(user_id)
    
    await update.message.reply_text(
        f"💰 <b>Bakiye:</b> {tokens:,} token\n\n"
        f"🍌 Nano Banana: 100 token/görsel\n\n"
        f"Token paketleri yakında gelecek!",
        reply_markup=back_button(),
        parse_mode="HTML"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    help_text = """
🤖 <b>Nano Banana AI Bot</b>

<b>Nasıl Kullanılır:</b>
1. "Fotoğraf Oluştur" butonuna tıklayın
2. "Nano Banana" seçin
3. Görsel açıklaması yazın
4. 100 token ödeyin
5. Görselinizi alın!

<b>Örnek Prompt'lar:</b>
• "Gün batımında İstanbul"
• "Kedi ve köpek arkadaş olmuş"
• "Futbol oynayan robot"
• "Uzayda Türk bayrağı"

<b>Token:</b>
• Yeni kullanıcı: 15.000 ücretsiz token
• Her görsel: 100 token
• Bakiye: /balance

<b>Demo Modu:</b>
Şu anda test aşamasındadır.
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
        await query.edit_message_text(
            text=f"👋 Ana menüye hoş geldiniz!\n💰 Bakiye: {tokens:,} token\n\n👇 Seçiminizi yapın:",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    
    elif data == "menu_image":
        tokens = db.get_user_tokens(user_id)
        await query.edit_message_text(
            text=f"🌄 <b>Fotoğraf Oluşturma</b>\n\n"
                 f"🍌 <b>Nano Banana</b> - AI ile görsel oluşturma\n"
                 f"🪙 Fiyat: 100 token/görsel\n"
                 f"💰 Bakiye: {tokens:,} token\n\n"
                 f"Hemen bir görsel oluşturmak için butona tıklayın:",
            reply_markup=image_generation_menu(),
            parse_mode="HTML"
        )
    
    elif data == "image_nano":
        await handle_nano_selection(query, user_id)
    
    elif data == "balance":
        tokens = db.get_user_tokens(user_id)
        await query.edit_message_text(
            text=f"💰 <b>Bakiye:</b> {tokens:,} token\n\n"
                 f"🍌 Nano Banana: 100 token/görsel\n\n"
                 f"Token paketleri yakında gelecek!",
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "history":
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
            tokens_change = item['tokens_change']
            details = item['details'][:30] if item['details'] else ""
            
            text += f"• {action}\n"
            text += f"  🪙 {tokens_change:+d} token\n"
            if details:
                text += f"  📝 {details}...\n"
            text += f"\n"
        
        await query.edit_message_text(
            text,
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "menu_llm":
        await query.edit_message_text(
            text="💬 <b>Dil Modelleri</b>\n\nChatGPT, Gemini, Claude yakında eklenecek!",
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "invite":
        bot_username = (await context.bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        
        await query.edit_message_text(
            text=f"🎁 <b>Arkadaşını Davet Et</b>\n\n"
                 f"Davet Linkin:\n<code>{ref_link}</code>\n\n"
                 f"Her davet için: 2.000 token bonus!\n"
                 f"Şu ana kadar: 0 kişi davet ettiniz.",
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "help":
        await help_command_callback(query)
    
    elif data == "cancel":
        await query.edit_message_text(
            text="❌ İşlem iptal edildi. Ana menüye dönülüyor...",
            reply_markup=back_button()
        )

async def handle_nano_selection(query, user_id):
    """Обработка выбора Nano Banana"""
    price = 100
    user_tokens = db.get_user_tokens(user_id)
    
    if user_tokens < price:
        await query.edit_message_text(
            text=f"❌ Yeterli token'ın yok!\n\n"
                 f"🍌 Nano Banana: {price} token\n"
                 f"💰 Mevcut bakiye: {user_tokens} token\n\n"
                 f"Token satın almak için /balance yazın\n"
                 f"Veya ücretsiz token için arkadaş davet edin.",
            reply_markup=back_button()
        )
        return
    
    await query.edit_message_text(
        text=f"🍌 <b>Nano Banana - Görsel Oluşturucu</b>\n\n"
             f"🪙 Fiyat: {price} token\n"
             f"💰 Bakiye: {user_tokens} token\n\n"
             f"<b>Şimdi görsel açıklaması yazın:</b>\n"
             f"Örnekler:\n"
             f"• 'Gün batımında İstanbul'\n"
             f"• 'Futbol oynayan robot'\n"
             f"• 'Uzayda Türk bayrağı'\n\n"
             f"<i>Lütfen bir mesaj olarak gönderin...</i>",
        reply_markup=cancel_button(),
        parse_mode="HTML"
    )

async def help_command_callback(query):
    """Callback для помощи"""
    help_text = """
🤖 <b>Nano Banana AI Bot</b>

<b>Kullanım:</b>
1. Ana menüden "Fotoğraf Oluştur"
2. "Nano Banana - Görsel Oluştur" butonu
3. Görsel açıklaması yazın
4. 100 token ödeyin
5. Görselinizi alın!

<b>Token:</b>
• Herkes: 15.000 ücretsiz token
• Her görsel: 100 token
• Bakiye kontrol: /balance

<b>Demo:</b>
Şu anda test aşamasında.
Gerçek API bağlantısı yakında!
    """
    
    await query.edit_message_text(
        help_text,
        reply_markup=back_button(),
        parse_mode="HTML"
    )

# ==================== ОБРАБОТКА ПРОМПТОВ ====================
async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка промпта для Nano Banana"""
    user_id = update.effective_user.id
    prompt = update.message.text.strip()
    
    if len(prompt) < 3:
        await update.message.reply_text(
            "❌ Lütfen en az 3 karakterlik bir açıklama yazın.",
            reply_markup=back_button()
        )
        return
    
    price = 100
    user_tokens = db.get_user_tokens(user_id)
    
    if user_tokens < price:
        await update.message.reply_text(
            f"❌ Yeterli token'ın yok!\n"
            f"Gereken: {price}, Mevcut: {user_tokens}",
            reply_markup=back_button()
        )
        return
    
    # Сообщение о начале генерации
    processing_msg = await update.message.reply_text(
        "⏳ Nano Banana ile görsel oluşturuluyor...\nLütfen 10-20 saniye bekleyin.",
        reply_markup=None
    )
    
    try:
        import os
        
        # Генерируем изображение
        image_path, tokens_spent, error = image_gen.generate_image(
            prompt=prompt,
            model_type="nano"
        )
        
        # Списание токенов
        db.add_tokens(user_id, -tokens_spent, "nano_banana", prompt[:50])
        
        # Добавляем запись в базу
        db.add_image_record(user_id, "🍌 Nano Banana", prompt, "local_file", tokens_spent)
        
        # Отправляем изображение
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=f"🎨 <b>🍌 Nano Banana</b>\n\n"
                           f"📝 <b>Açıklama:</b> {prompt}\n"
                           f"🪙 <b>Token:</b> {tokens_spent}\n"
                           f"💰 <b>Kalan bakiye:</b> {db.get_user_tokens(user_id):,}\n\n"
                           f"<i>Demo modu - Gerçek API yakında!</i>\n"
                           f"Yeni görsel için /start",
                    parse_mode="HTML",
                    reply_markup=back_button()
                )
            
            # Удаляем временный файл
            try:
                os.remove(image_path)
            except:
                pass
        
        # Удаляем сообщение "обработка"
        await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        await processing_msg.edit_text(
            f"❌ Bir hata oluştu!\nHata: {str(e)[:100]}",
            reply_markup=back_button()
        )

# ==================== ЗАПУСК БОТА ====================
def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN bulunamadı!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчики текстовых сообщений
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_prompt
    ))
    
    # Запуск
    logger.info("✅ 🤖 Nano Banana Bot başlatılıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
