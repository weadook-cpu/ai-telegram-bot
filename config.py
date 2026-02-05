# config.py
class Config:
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    ADMIN_ID = "YOUR_TELEGRAM_ID"
    
    DEFAULT_TOKENS = 15000
    
    PRICES = {
        "nano_banana": 100,
        "nano_banana_pro": 200,
        "gpt_image": 150,
        "midjourney": 300,
        "recraft": 250,
        "chatgpt": 10,
        "gemini": 10,
        "claude": 15,
        "deepseek": 5,
        "grok": 20,
        "veo": 500,
        "sora": 600,
        "kling": 400,
        "suno": 300
    }
    
    TEXTS = {
        "welcome": "👋 Merhaba! Bakiyende {tokens} token var – bunları yapay zeka sorguları için kullanabilirsin.",
        "balance": "💰 Bakiye: {tokens} token",
        "no_tokens": "❌ Yeterli token'ın yok! Bakiye: {tokens} token",
        "processing": "⏳ İşleniyor... Lütfen bekleyin.",
        "success": "✅ Tamamlandı!",
        "error": "❌ Bir hata oluştu. Lütfen tekrar deneyin.",
        "menu": "👇 Aşağıdaki menüden bir seçenek seçin:"
    }
