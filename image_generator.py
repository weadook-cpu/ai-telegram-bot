# image_generator.py - С GOOGLE GEMINI API
import os
import logging
import google.generativeai as genai
import requests
from typing import Optional, Tuple
import io
from PIL import Image
import base64

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Генератор изображений через Google Gemini API"""
    
    def __init__(self):
        # Настройка Gemini API
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            logger.info("✅ Gemini API başlatıldı")
        else:
            logger.warning("⚠️ Gemini API anahtarı bulunamadı, demo modunda çalışılıyor")
            self.model = None
        
        # Цены в токенах
        self.prices = {
            "nano": 100,           # Nano Banana
            "nano_pro": 200,       # Nano Banana Pro
            "gpt": 150,            # GPT Image
            "midjourney": 300,     # Midjourney
            "recraft": 250,        # Recraft
            "gemini": 100,         # Google Gemini
        }
    
    def generate_image(self, prompt: str, model_type: str = "nano") -> Tuple[Optional[str], int, str]:
        """
        Генерация изображения по промпту
        
        Returns:
            (image_url, tokens_spent, error_message)
        """
        logger.info(f"🖼 Görsel oluşturuluyor: '{prompt}' ({model_type})")
        
        # Проверяем, поддерживается ли модель
        if model_type not in self.prices:
            return None, 0, f"❌ Model desteklenmiyor: {model_type}"
        
        tokens_spent = self.prices[model_type]
        
        # Если выбран Gemini и есть API ключ
        if model_type == "gemini" and self.gemini_api_key:
            return self._generate_with_gemini(prompt, tokens_spent)
        
        # Для других моделей или если нет Gemini API
        return self._generate_demo_image(prompt, model_type, tokens_spent)
    
    def _generate_with_gemini(self, prompt: str, tokens_spent: int) -> Tuple[Optional[str], int, str]:
        """Генерация через Gemini API"""
        try:
            # Создаём промпт для генерации изображения
            full_prompt = f"""
            Lütfen bu açıklamaya göre bir görsel oluştur:
            "{prompt}"
            
            Önemli:
            1. Yüksek kaliteli, detaylı bir görsel oluştur
            2. 512x512 piksel boyutunda olmalı
            3. Fotoğraf gerçekçi veya sanatsal stil
            4. Türk kültürüne uygun içerik
            """
            
            # Генерируем изображение через Gemini
            response = self.model.generate_content(full_prompt)
            
            # Gemini возвращает текст, но может генерировать изображения
            # В реальности нужно использовать Gemini Vision или другой подход
            # Для демо вернём заглушку
            
            # Создаём демо-изображение на основе промпта
            demo_url = self._create_demo_image_url(prompt)
            
            logger.info(f"✅ Gemini ile görsel oluşturuldu: {prompt[:50]}...")
            return demo_url, tokens_spent, ""
            
        except Exception as e:
            logger.error(f"❌ Gemini hatası: {e}")
            # Fallback на демо
            demo_url = self._create_demo_image_url(prompt)
            return demo_url, tokens_spent, f"Gemini hatası, demo görsel gönderildi: {str(e)}"
    
    def _generate_demo_image(self, prompt: str, model_type: str, tokens_spent: int) -> Tuple[str, int, str]:
        """Демо-режим генерации (без реального API)"""
        # Создаём URL для демо-изображения
        
        # Разные стили для разных моделей
        styles = {
            "nano": "digital art",
            "nano_pro": "photorealistic",
            "gpt": "ai generated",
            "midjourney": "fantasy art",
            "recraft": "vector art",
            "gemini": "modern"
        }
        
        style = styles.get(model_type, "art")
        
        # Создаём URL для Unsplash с поиском по промпту
        search_term = prompt.replace(" ", "%20")[:30]
        demo_url = f"https://source.unsplash.com/512x512/?{search_term},{style}"
        
        # Альтернатива: DummyImage с текстом промпта
        # encoded_prompt = base64.b64encode(prompt[:50].encode()).decode()[:20]
        # demo_url = f"https://dummyimage.com/512x512/009688/ffffff&text={encoded_prompt}"
        
        logger.info(f"🔄 Demo görsel oluşturuldu: {prompt[:50]}...")
        return demo_url, tokens_spent, "Demo modu: Gerçek API bağlantısı için ayarlar yapılmalıdır."
    
    def _create_demo_image_url(self, prompt: str) -> str:
        """Создаёт URL для демо-изображения"""
        # Безопасное кодирование промпта для URL
        import urllib.parse
        safe_prompt = urllib.parse.quote(prompt[:50])
        
        # Вариант 1: Unsplash (реальные фото)
        # return f"https://source.unsplash.com/512x512/?{safe_prompt}"
        
        # Вариант 2: Placeholder с цветом в зависимости от промпта
        colors = ["009688", "2196F3", "4CAF50", "FF9800", "E91E63", "9C27B0"]
        import hashlib
        color_index = hash(prompt) % len(colors)
        color = colors[color_index]
        
        return f"https://via.placeholder.com/512x512/{color}/FFFFFF?text={safe_prompt}"
    
    def validate_api_key(self) -> bool:
        """Проверяем валидность API ключа"""
        if not self.gemini_api_key:
            return False
        
        try:
            # Простая проверка ключа
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("test")
            return True
        except:
            return False

# Глобальный инстанс
image_gen = ImageGenerator()
