# bot.py - NANO BANANA BOT (DEMO)
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
        [InlineKeyboardButton("🍌 Nano Banana - Görsel Oluştur", callback_data="menu_image")],
        [InlineKeyboardButton("💰 Bakiye Sorgula", callback_data="balance")],
        [InlineKeyboardButton("📊 İşlem Geçmişi", callback_data="history")],
        [InlineKeyboardButton("🎁 Arkadaş Davet", callback_data="invite")],
        [InlineKeyboardButton("ℹ️ Yardım", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button():
    keyboard = [[InlineKeyboardButton("🔙 Ana Menü", callback_data="back_to_main")]]
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
    
    # Добавляем пользователя в базу (15.000 токенов)
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        invited_by=invited_by
    )
    
    # Получаем баланс (всегда 15.000+ в демо)
    tokens = db.get_user_tokens(user.id)
    
    welcome_text = (
        f"👋 Merhaba {user.first_name or ''}!\n"
        f"🤖 **Nano Banana AI Bot**'a hoş geldin!\n\n"
        f"💰 **Başlangıç bakiyen:** {tokens:,} token\n"
        f"🎨 Her görsel: 100 token\n\n"
        f"👇 Aşağıdaki menüden seçim yapın:"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать баланс"""
    user_id = update.effective_user.id
    tokens = db.get_user_tokens(user_id)
    
    await update.message.reply_text(
        f"💰 **Bakiye Durumu**\n\n"
        f"🪙 Mevcut token: **{tokens:,}**\n"
        f"🍌 Nano Banana: **100 token** / görsel\n\n"
        f"💡 Her yeni kullanıcı 15.000 ücretsiz token alır!\n"
        f"👥 Arkadaş davet et, ekstra token kazan!",
        reply_markup=back_button(),
        parse_mode="HTML"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    help_text = """
🤖 **Nano Banana AI Bot - Yardım**

🎨 **Görsel Oluşturma:**
1. Ana menüden "Nano Banana" seç
2. Görsel açıklaması yaz (Türkçe/İngilizce)
3. 100 token öde
4. Görselini al!

💡 **Örnek Açıklamalar:**
• "Gün batımında İstanbul"
• "Futbol oynayan robot"
• "Uzayda Türk bayrağı"
• "Orman içinde şelale"

🪙 **Token Sistemi:**
• Başlangıç: 15.000 ücretsiz token
• Her görsel: 100 token
• Bakiye kontrol: /balance

🚀 **Demo Modu:**
Şu anda test aşamasındayız.
Gerçek AI API bağlantısı yakında eklenecek!
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
            text=f"🏠 **Ana Menü**\n\n💰 Bakiye: {tokens:,} token\n\n👇 Seçiminizi yapın:",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    
    elif data == "menu_image":
        tokens = db.get_user_tokens(user_id)
        await query.edit_message_text(
            text=f"🎨 **Nano Banana - AI Görsel Oluşturucu**\n\n"
                 f"🪙 Fiyat: **100 token** / görsel\n"
                 f"💰 Bakiye: **{tokens:,} token**\n\n"
                 f"**Hemen bir görsel oluşturmak için butona tıklayın:**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🍌 GÖRSEL OLUŞTUR", callback_data="generate_image")],
                [InlineKeyboardButton("🔙 Ana Menü", callback_data="back_to_main")]
            ]),
            parse_mode="HTML"
        )
    
    elif data == "generate_image":
        await handle_generate_image(query, user_id)
    
    elif data == "balance":
        tokens = db.get_user_tokens(user_id)
        await query.edit_message_text(
            text=f"💰 **Bakiye Durumu**\n\n"
                 f"🪙 Mevcut token: **{tokens:,}**\n"
                 f"🍌 Nano Banana: **100 token** / görsel\n\n"
                 f"💡 Yeni özellikler yakında!",
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "history":
        history = db.get_user_history(user_id)
        
        if not history:
            await query.edit_message_text(
                "📭 Henüz işlem geçmişiniz yok.\nİlk görselinizi oluşturun!",
                reply_markup=back_button()
            )
            return
        
        text = "📊 **Son İşlemleriniz:**\n\n"
        for item in history[:5]:
            action = item['action']
            tokens_change = item['tokens_change']
            details = item['details'][:30] if item['details'] else ""
            
            emoji = "🔼" if tokens_change > 0 else "🔽"
            text += f"{emoji} **{action}**\n"
            text += f"   🪙 {tokens_change:+d} token\n"
            if details:
                text += f"   📝 {details}...\n"
            text += f"\n"
        
        await query.edit_message_text(
            text,
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "invite":
        bot_username = (await context.bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        
        await query.edit_message_text(
            text=f"🎁 **Arkadaşını Davet Et**\n\n"
                 f"**Davet Linkin:**\n`{ref_link}`\n\n"
                 f"✅ **Her davet için:** 2.000 token bonus!\n"
                 f"✅ **Arkadaşın satın alımından:** %20 komisyon\n\n"
                 f"📈 **Şu ana kadar:** 0 kişi davet ettiniz\n"
                 f"🪙 **Kazandığın token:** 0",
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "help":
        await query.edit_message_text(
            text=help_command.__doc__.replace("    ", ""),
            reply_markup=back_button(),
            parse_mode="HTML"
        )
    
    elif data == "cancel":
        await query.edit_message_text(
            text="❌ İşlem iptal edildi. Ana menüye yönlendiriliyorsunuz...",
            reply_markup=back_button()
        )

async def handle_generate_image(query, user_id):
    """Обработка запроса на генерацию изображения"""
    price = 100
    user_tokens = db.get_user_tokens(user_id)
    
    if user_tokens < price:
        await query.edit_message_text(
            text=f"❌ **Yeterli token'ın yok!**\n\n"
                 f"🍌 Nano Banana: {price} token\n"
                 f"💰 Mevcut bakiye: {user_tokens} token\n\n"
                 f"💡 Ücretsiz token almak için:\n"
                 f"• Arkadaş davet et (/start link gönder)\n"
                 f"• Token paketleri (yakında)",
            reply_markup=back_button()
        )
        return
    
    await query.edit_message_text(
        text=f"🎨 **Görsel Açıklaması Yazın**\n\n"
             f"🍌 **Nano Banana** AI görsel oluşturucu\n"
             f"🪙 **Fiyat:** {price} token\n"
             f"💰 **Bakiye:** {user_tokens:,} token\n\n"
             f"**Lütfen istediğiniz görseli tarif edin:**\n"
             f"Örnekler:\n"
             f"• 'Gün batımında İstanbul manzarası'\n"
             f"• 'Robot elma yiyor'\n"
             f"• 'Deniz kenarında romantik çift'\n\n"
             f"✍️ **Açıklamanızı mesaj olarak gönderin...**",
        reply_markup=cancel_button(),
        parse_mode="HTML"
    )

# ==================== ОБРАБОТКА ПРОМПТОВ ====================
async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка промпта для генерации изображения"""
    user_id = update.effective_user.id
    prompt = update.message.text.strip()
    
    if len(prompt) < 3:
        await update.message.reply_text(
            "❌ Lütfen en az 3 karakterlik bir açıklama yazın.\nÖrnek: 'Güneşli bir gün'",
            reply_markup=back_button()
        )
        return
    
    price = 100
    user_tokens = db.get_user_tokens(user_id)
    
    # Проверка баланса (в демо всегда должно хватать)
    if user_tokens < price:
        await update.message.reply_text(
            f"⚠️ **Demo Modu Uyarısı**\n\n"
            f"Normalde {price} token gerekiyor.\n"
            f"Ama demo modunda devam ediyoruz!\n\n"
            f"⏳ Görsel oluşturuluyor...",
            reply_markup=back_button()
        )
    
    # Сообщение о начале генерации
    processing_msg = await update.message.reply_text(
        "⏳ **Nano Banana görsel oluşturuyor...**\n"
        "Lütfen 5-10 saniye bekleyin.",
        reply_markup=None
    )
    
    try:
        # Генерируем изображение (демо-режим)
        image_url, tokens_spent, error = image_gen.generate_image(
            prompt=prompt,
            model_type="nano"
        )
        
        if error:
            await processing_msg.edit_text(
                f"⚠️ Demo: {error}\n\nGörsel gönderiliyor...",
                reply_markup=back_button()
            )
        
        # "Списываем" токены (в демо только логируем)
        db.add_tokens(user_id, -tokens_spent, "image_generation", 
                     f"Nano Banana: {prompt[:50]}...")
        
        # Добавляем запись в базу
        db.add_image_record(user_id, "🍌 Nano Banana", prompt, image_url, tokens_spent)
        
        # Отправляем изображение
        await update.message.reply_photo(
            photo=image_url,
            caption=f"🎨 **🍌 Nano Banana**\n\n"
                   f"📝 **Açıklama:** {prompt}\n"
                   f"🪙 **Harcanan token:** {tokens_spent}\n"
                   f"💰 **Kalan bakiye:** {db.get_user_tokens(user_id):,}\n\n"
                   f"⭐ **Demo Modu** - Gerçek AI API yakında!\n"
                   f"🔄 Yeni görsel için /start",
            parse_mode="HTML",
            reply_markup=back_button()
        )
        
        # Удаляем сообщение "обработка"
        await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"❌ Generation error: {e}")
        
        # Fallback - отправляем статичное изображение
        fallback_url = "https://images.unsplash.com/photo-1554080353-a576cf803bda?w=512&h=512&fit=crop"
        
        await update.message.reply_photo(
            photo=fallback_url,
            caption=f"🎨 **🍌 Nano Banana**\n\n"
                   f"📝 **Açıklama:** {prompt}\n"
                   f"🪙 **Harcanan token:** 100\n"
                   f"💰 **Kalan bakiye:** {db.get_user_tokens(user_id):,}\n\n"
                   f"⚠️ **Demo Görsel** - Sistem test aşamasında\n"
                   f"🔧 Gerçek AI API çok yakında!",
            parse_mode="HTML",
            reply_markup=back_button()
        )
        
        try:
            await processing_msg.delete()
        except:
            pass

# ==================== ЗАПУСК БОТА ====================
def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN bulunamadı!")
        logger.error("Railway → Variables → BOT_TOKEN ekleyin")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчики текстовых сообщений (промпты)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_prompt
    ))
    
    # Запуск
    logger.info("✅ 🤖 Nano Banana AI Bot başlatılıyor...")
    logger.info("✅ 🎨 Demo modu aktif")
    logger.info("✅ 💰 Her kullanıcıya 15.000 token")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
