# bot.py
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Наши модули
from config import Config
from database import Database
from keyboards import Keyboards

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
db = Database()

class AITelegramBot:
    def __init__(self):
        self.token = os.getenv("BOT_TOKEN", Config.BOT_TOKEN)
        self.app = Application.builder().token(self.token).build()
        
        # Регистрация обработчиков
        self.register_handlers()
    
    def register_handlers(self):
        """Регистрация всех обработчиков"""
        # Команды
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("balance", self.balance_command))
        self.app.add_handler(CommandHandler("history", self.history_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        # Обработчики кнопок
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Обработчики сообщений
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_handler))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user = update.effective_user
        user_id = user.id
        
        # Получаем реферальный ID из параметра
        invited_by = None
        if context.args:
            try:
                invited_by = int(context.args[0])
            except ValueError:
                pass
        
        # Добавляем пользователя в базу
        db.add_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            invited_by=invited_by
        )
        
        # Получаем баланс
        tokens = db.get_user_tokens(user_id)
        
        # Приветственное сообщение
        welcome_text = Config.TEXTS["welcome"].format(tokens=tokens)
        menu_text = Config.TEXTS["menu"]
        
        await update.message.reply_text(
            f"{welcome_text}\n\n{menu_text}",
            reply_markup=Keyboards.main_menu(),
            parse_mode="HTML"
        )
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать баланс"""
        user_id = update.effective_user.id
        tokens = db.get_user_tokens(user_id)
        
        balance_text = f"💰 <b>Bakiye:</b> {tokens} token\n\n"
        balance_text += "Token paketlerini satın almak için butona tıklayın:"
        
        await update.message.reply_text(
            balance_text,
            reply_markup=Keyboards.buy_tokens_menu(),
            parse_mode="HTML"
        )
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать историю операций"""
        user_id = update.effective_user.id
        history = db.get_user_history(user_id, limit=10)
        
        if not history:
            await update.message.reply_text(
                "📭 Henüz işlem geçmişiniz yok.",
                reply_markup=Keyboards.back_button()
            )
            return
        
        history_text = "📊 <b>Son 10 İşleminiz:</b>\n\n"
        for action, tokens_used, details, timestamp in history:
            date_str = timestamp.strftime("%d.%m.%Y %H:%M")
            history_text += f"▫️ {action}\n"
            history_text += f"   🔸 Token: {tokens_used}\n"
            history_text += f"   🕐 {date_str}\n"
            if details:
                history_text += f"   📝 {details[:50]}...\n"
            history_text += "\n"
        
        await update.message.reply_text(
            history_text,
            reply_markup=Keyboards.back_button(),
            parse_mode="HTML"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Помощь"""
        help_text = """
🤖 <b>AI Telegram Bot - Yardım</b>

<b>Kullanım:</b>
1. Menüden bir araç seçin
2. İsteklerinizi yazın/girin
3. Token'larınızla ödeme yapın
4. Sonucu alın!

<b>Token Sistemi:</b>
• Her yeni kullanıcıya 15.000 ücretsiz token verilir
• Her işlem belirli sayıda token kullanır
• Token'larınız biterse satın alabilirsiniz

<b>Destek:</b>
Sorularınız için @kullanıcı_adı ile iletişime geçin.
        """
        
        await update.message.reply_text(
            help_text,
            reply_markup=Keyboards.back_button(),
            parse_mode="HTML"
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        data = query.data
        
        # Обработка разных кнопок
        if data == "back_to_main":
            tokens = db.get_user_tokens(user_id)
            welcome_text = Config.TEXTS["welcome"].format(tokens=tokens)
            
            await query.edit_message_text(
                text=f"{welcome_text}\n\n{Config.TEXTS['menu']}",
                reply_markup=Keyboards.main_menu(),
                parse_mode="HTML"
            )
        
        elif data == "menu_llm":
            await query.edit_message_text(
                text="💬 <b>Dil Modelleri</b>\n\nHangi modeli kullanmak istiyorsunuz?",
                reply_markup=Keyboards.language_models_menu(),
                parse_mode="HTML"
            )
        
        elif data == "menu_image":
            await query.edit_message_text(
                text="🌄 <b>Fotoğraf Oluşturma Araçları</b>\n\nHangi aracı kullanmak istiyorsunuz?",
                reply_markup=Keyboards.image_generation_menu(),
                parse_mode="HTML"
            )
        
        elif data == "menu_video":
            await query.edit_message_text(
                text="📹 <b>Video Oluşturma Araçları</b>\n\nHangi aracı kullanmak istiyorsunuz?",
                reply_markup=Keyboards.video_generation_menu(),
                parse_mode="HTML"
            )
        
        elif data == "menu_audio":
            await query.edit_message_text(
                text="🎙 <b>Ses Araçları</b>\n\nHangi aracı kullanmak istiyorsunuz?",
                reply_markup=Keyboards.audio_tools_menu(),
                parse_mode="HTML"
            )
        
        elif data == "balance":
            tokens = db.get_user_tokens(user_id)
            balance_text = f"💰 <b>Bakiye:</b> {tokens} token\n\n"
            balance_text += "Token paketlerini satın almak için butona tıklayın:"
            
            await query.edit_message_text(
                text=balance_text,
                reply_markup=Keyboards.buy_tokens_menu(),
                parse_mode="HTML"
            )
        
        elif data == "history":
            await self.show_history(query, user_id)
        
        elif data == "invite":
            bot_username = context.bot.username
            referral_link = f"https://t.me/{bot_username}?start={user_id}"
            
            invite_text = f"""
🎁 <b>Arkadaşını Davet Et</b>

Davet bağlantın:
{referral_link}

<b>Kazançlar:</b>
• Her davet ettiğin arkadaş için: 2.000 token
• Arkadaşının ilk satın alımından: %20 komisyon

<b>Davet ettiğin kişiler:</b> 0
<b>Kazandığın token:</b> 0
            """
            
            await query.edit_message_text(
                text=invite_text,
                reply_markup=Keyboards.back_button(),
                parse_mode="HTML"
            )
        
        elif data.startswith("model_"):
            model_name = data.replace("model_", "")
            await self.handle_model_selection(query, user_id, model_name)
        
        elif data.startswith("image_"):
            model_name = data.replace("image_", "")
            await self.handle_image_selection(query, user_id, model_name)
        
        elif data.startswith("buy_"):
            package = data.replace("buy_", "")
            await self.handle_purchase(query, user_id, package)
    
    async def show_history(self, query, user_id):
        """Показать историю в inline-режиме"""
        history = db.get_user_history(user_id, limit=10)
        
        if not history:
            await query.edit_message_text(
                text="📭 Henüz işlem geçmişiniz yok.",
                reply_markup=Keyboards.back_button()
            )
            return
        
        history_text = "📊 <b>Son 10 İşleminiz:</b>\n\n"
        for action, tokens_used, details, timestamp in history:
            date_str = timestamp.strftime("%d.%m.%Y %H:%M")
            history_text += f"▫️ {action}\n"
            history_text += f"   🔸 Token: {tokens_used}\n"
            history_text += f"   🕐 {date_str}\n"
            if details:
                history_text += f"   📝 {details[:50]}...\n"
            history_text += "\n"
        
        await query.edit_message_text(
            text=history_text,
            reply_markup=Keyboards.back_button(),
            parse_mode="HTML"
        )
    
    async def handle_model_selection(self, query, user_id, model_name):
        """Обработка выбора языковой модели"""
        models = {
            "chatgpt": "ChatGPT",
            "gemini": "Google Gemini",
            "claude": "Anthropic Claude",
            "deepseek": "DeepSeek",
            "grok": "Grok"
        }
        
        model_display = models.get(model_name, model_name)
        price = Config.PRICES.get(model_name, 10)
        
        text = f"""
💬 <b>{model_display}</b>

<b>Fiyat:</b> {price} token/soru
<b>Mevcut bakiye:</b> {db.get_user_tokens(user_id)} token

Lütfen sorunuzu yazın:
        """
        
        await query.edit_message_text(
            text=text,
            reply_markup=Keyboards.back_button(),
            parse_mode="HTML"
        )
        
        # Сохраняем выбранную модель в контекст
        context = query.message
        context.model_selected = model_name
    
    async def handle_image_selection(self, query, user_id, model_name):
        """Обработка выбора модели генерации изображений"""
        models = {
            "nano": "🍌 Nano Banana",
            "nano_pro": "⭐ Nano Banana Pro",
            "gpt": "🖼 GPT Image 1.5",
            "midjourney": "🎨 Midjourney",
            "recraft": "✨ Recraft"
        }
        
        model_display = models.get(model_name, model_name)
        price = Config.PRICES.get(f"{model_name}_{'pro' if 'pro' in model_name else ''}".rstrip('_'), 100)
        
        text = f"""
🌄 <b>{model_display}</b>

<b>Fiyat:</b> {price} token/görsel
<b>Mevcut bakiye:</b> {db.get_user_tokens(user_id)} token

Lütfen görsel için açıklama (prompt) yazın:
Örnek: "Gün batımında İstanbul manzarası"
        """
        
        await query.edit_message_text(
            text=text,
            reply_markup=Keyboards.back_button(),
            parse_mode="HTML"
        )
        
        # Сохраняем выбранную модель в контекст
        context = query.message
        context.image_model_selected = model_name
    
    async def handle_purchase(self, query, user_id, package):
        """Обработка покупки токенов"""
        packages = {
            "5000": (5000, 49),
            "15000": (15000, 129),
            "50000": (50000, 399)
        }
        
        if package not in packages:
            await query.edit_message_text(
                text="❌ Geçersiz paket seçimi.",
                reply_markup=Keyboards.back_button()
            )
            return
        
        tokens, price = packages[package]
        
        text = f"""
💰 <b>Token Paketi Satın Al</b>

<b>Paket:</b> {tokens:,} token
<b>Fiyat:</b> {price} TL

Ödeme yöntemini seçin:
        """
        
        await query.edit_message_text(
            text=text,
            reply_markup=Keyboards.back_button(),
            parse_mode="HTML"
        )
    
    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Здесь будет логика обработки промптов для разных моделей
        # Пока просто отвечаем
        
        reply_text = f"""
📝 İsteğiniz alındı:

"{message_text}"

Bu özellik şu anda geliştirme aşamasındadır. Yakında kullanıma açılacak!
        """
        
        await update.message.reply_text(
            reply_text,
            reply_markup=Keyboards.back_button(),
            parse_mode="HTML"
        )
    
    def run(self):
        """Запуск бота"""
        logger.info("🤖 AI Telegram Bot başlatılıyor...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = AITelegramBot()
    bot.run()
