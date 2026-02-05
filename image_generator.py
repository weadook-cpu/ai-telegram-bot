# image_generator.py - УПРОЩЕННАЯ ВЕРСИЯ
import os
import logging
import random
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Генератор изображений (упрощённая демо-версия)"""
    
    def __init__(self):
        self.prices = {
            "nano": 100,
            "nano_pro": 200,
            "gpt": 150,
            "midjourney": 300,
            "recraft": 250,
        }
        
        # Демо-изображения (реальные URL)
        self.demo_images = [
            "https://images.unsplash.com/photo-1494790108755-2616b612b786",  # Женщина
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",  # Мужчина
            "https://images.unsplash.com/photo-1534528741775-53994a69daeb",  # Портрет
            "https://images.unsplash.com/photo-1517841905240-472988babdf9",  # Девушка
            "https://images.unsplash.com/photo-1524504388940-b1c1722653e1",  # Модель
            "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde",  # Бизнес
            "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e",  # Девушка в желтом
            "https://images.unsplash.com/photo-1544005313-94ddf0286df2",  # Девушка в белом
            "https://images.unsplash.com/photo-1552058544-f2b08422138a",  # Улыбка
            "https://images.unsplash.com/photo-1544725176-7c40e5a71c5e",  # Девушка в свитере
        ]
    
    def generate_image(self, prompt: str, model_type: str = "nano") -> Tuple[str, int, str]:
        """Генерация изображения - возвращаем URL демо-изображения"""
        logger.info(f"🖼 Demo görsel: '{prompt[:50]}...'")
        
        if model_type not in self.prices:
            return "", 0, f"❌ Model desteklenmiyor: {model_type}"
        
        tokens_spent = self.prices[model_type]
        
        # Выбираем случайное демо-изображение
        image_url = random.choice(self.demo_images) + "?w=512&h=512&fit=crop"
        
        # Анализируем промпт для выбора подходящего изображения
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["kadın", "kız", "bayan", "woman", "female"]):
            # Женские изображения
            female_images = [
                "https://images.unsplash.com/photo-1494790108755-2616b612b786",
                "https://images.unsplash.com/photo-1534528741775-53994a69daeb", 
                "https://images.unsplash.com/photo-1517841905240-472988babdf9",
                "https://images.unsplash.com/photo-1524504388940-b1c1722653e1",
                "https://images.unsplash.com/photo-1544005313-94ddf0286df2",
            ]
            image_url = random.choice(female_images) + "?w=512&h=512&fit=crop"
        
        elif any(word in prompt_lower for word in ["erkek", "adam", "man", "male"]):
            # Мужские изображения
            male_images = [
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
                "https://images.unsplash.com/photo-1500648767791-00dcc994a43e",
                "https://images.unsplash.com/photo-1507591064344-4c6ce005-128",
            ]
            image_url = random.choice(male_images) + "?w=512&h=512&fit=crop"
        
        elif any(word in prompt_lower for word in ["doğa", "manzara", "nature", "landscape"]):
            # Пейзажи
            image_url = "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=512&h=512&fit=crop"
        
        elif any(word in prompt_lower for word in ["ev", "oda", "interior", "house"]):
            # Интерьеры
            image_url = "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=512&h=512&fit=crop"
        
        logger.info(f"✅ Demo görsel URL: {image_url}")
        return image_url, tokens_spent, "Demo modu: Gerçek API için hazırlanıyor..."

# Глобальный инстанс
image_gen = ImageGenerator()
