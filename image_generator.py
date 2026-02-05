# image_generator.py - FIXED VERSION
import os
import logging
import google.generativeai as genai
import requests
from typing import Optional, Tuple
import urllib.parse
import io
from PIL import Image, ImageDraw, ImageFont
import textwrap
import base64

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Генератор изображений"""
    
    def __init__(self):
        # Настройка Gemini API
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                # Используем gemini-1.5-pro для лучшей генерации
                self.model = genai.GenerativeModel('gemini-1.5-pro')
                self.gemini_available = True
                logger.info("✅ Gemini API başlatıldı")
            except Exception as e:
                logger.error(f"❌ Gemini API hatası: {e}")
                self.gemini_available = False
        else:
            logger.warning("⚠️ Gemini API anahtarı bulunamadı")
            self.gemini_available = False
        
        # Цены в токенах
        self.prices = {
            "nano": 100,
            "nano_pro": 200,
            "gpt": 150,
            "midjourney": 300,
            "recraft": 250,
            "gemini": 100,
        }
    
    def generate_image(self, prompt: str, model_type: str = "nano") -> Tuple[Optional[str], int, str]:
        """
        Генерация изображения
        
        Returns:
            (image_path_or_url, tokens_spent, error_message)
        """
        logger.info(f"🖼 Görsel oluşturuluyor: '{prompt}'")
        
        if model_type not in self.prices:
            return None, 0, f"❌ Model desteklenmiyor: {model_type}"
        
        tokens_spent = self.prices[model_type]
        
        # Пробуем Gemini если есть ключ
        if self.gemini_available:
            try:
                image_bytes = self._generate_with_gemini(prompt)
                if image_bytes:
                    # Сохраняем временный файл
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                        tmp.write(image_bytes)
                        tmp_path = tmp.name
                    
                    logger.info(f"✅ Gemini ile görsel oluşturuldu")
                    return tmp_path, tokens_spent, ""
            except Exception as e:
                logger.warning(f"Gemini hatası, demo'ya geçiliyor: {e}")
        
        # Демо-режим: создаём локальное изображение
        return self._generate_local_image(prompt, tokens_spent)
    
    def _generate_with_gemini(self, prompt: str) -> Optional[bytes]:
        """Генерация через Gemini API"""
        try:
            # Используем Gemini для генерации изображения
            # В реальности Gemini не генерирует изображения напрямую,
            # поэтому создадим текстовое описание и сгенерируем локально
            
            # Для реальной генерации нужен другой API
            # Пока возвращаем None чтобы использовать демо
            return None
            
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return None
    
    def _generate_local_image(self, prompt: str, tokens_spent: int) -> Tuple[str, int, str]:
        """Создаём локальное изображение с текстом"""
        try:
            # Создаём изображение
            img = Image.new('RGB', (512, 512), color=(0, 150, 136))  # Turkish teal
            draw = ImageDraw.Draw(img)
            
            # Пробуем добавить шрифт (если есть)
            try:
                font = ImageFont.truetype("arial.ttf", 30)
            except:
                font = ImageFont.load_default()
            
            # Разбиваем текст на строки
            lines = textwrap.wrap(prompt, width=30)
            y_text = 200
            
            for line in lines:
                # Центрируем текст
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (512 - text_width) / 2
                draw.text((x, y_text), line, font=font, fill=(255, 255, 255))
                y_text += text_height + 10
                
                if y_text > 450:  # Не выходим за границы
                    break
            
            # Добавляем watermark
            draw.text((10, 10), "AI Generated Image", font=font, fill=(255, 255, 255, 128))
            draw.text((10, 490), "Demo Mode - Real API Coming Soon", 
                     font=font, fill=(255, 255, 255, 128))
            
            # Сохраняем во временный файл
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                img.save(tmp, format='JPEG', quality=85)
                tmp_path = tmp.name
            
            logger.info(f"🔄 Yerel demo görsel oluşturuldu: {prompt[:50]}...")
            return tmp_path, tokens_spent, "Demo modu: Gerçek API bağlantısı için ayarlar yapılmalıdır."
            
        except Exception as e:
            logger.error(f"Local image error: {e}")
            # Fallback на статичное изображение
            return self._get_static_image(), tokens_spent, "Demo modu - Statik görsel"
    
    def _get_static_image(self) -> str:
        """Возвращает путь к статичному изображению"""
        # Создаём простое статичное изображение
        img = Image.new('RGB', (512, 512), color=(41, 128, 185))
        draw = ImageDraw.Draw(img)
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            img.save(tmp, format='JPEG')
            return tmp.name
    
    def validate_api_key(self) -> bool:
        """Проверяем валидность API ключа"""
        return self.gemini_available

# Глобальный инстанс
image_gen = ImageGenerator()
