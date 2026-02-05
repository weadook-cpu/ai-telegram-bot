# image_generator.py - ДЕМО С РЕАЛЬНЫМИ ИЗОБРАЖЕНИЯМИ
import os
import logging
import random
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Генератор изображений (демо с Unsplash)"""
    
    def __init__(self):
        self.prices = {
            "nano": 100,
            "nano_pro": 200,
            "gpt": 150,
            "midjourney": 300,
            "recraft": 250,
        }
        
        # Коллекция реальных изображений с Unsplash
        self.image_collection = {
            "woman": [
                "https://images.unsplash.com/photo-1494790108755-2616b612b786",  # Улыбающаяся женщина
                "https://images.unsplash.com/photo-1534528741775-53994a69daeb",  # Портрет в шляпе
                "https://images.unsplash.com/photo-1517841905240-472988babdf9",  # Девушка с веснушками
                "https://images.unsplash.com/photo-1544005313-94ddf0286df2",    # Девушка в белом
                "https://images.unsplash.com/photo-1524504388940-b1c1722653e1",  # Модель
                "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df",  # Девушка с темными волосами
                "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f",  # Женщина в желтом
            ],
            "man": [
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",  # Мужчина
                "https://images.unsplash.com/photo-1500648767791-00dcc994a43e",  # Мужчина в очках
                "https://images.unsplash.com/photo-1507591064344-4c6ce005-128",  # Бизнесмен
            ],
            "nature": [
                "https://images.unsplash.com/photo-1501854140801-50d01698950b",  # Горы
                "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05",  # Лес
                "https://images.unsplash.com/photo-1519681393784-d120267933ba",  # Закат
            ],
            "interior": [
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688",  # Интерьер
                "https://images.unsplash.com/photo-1513584684374-8bab748fbf90",  # Деревянный интерьер
                "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e",  # Уютная комната
            ],
            "default": [
                "https://images.unsplash.com/photo-1554080353-a576cf803bda",    # Фотоаппарат
                "https://images.unsplash.com/photo-1516035069371-29a1b244cc32",  # Город
                "https://images.unsplash.com/photo-1518834103328-5d0d4b48f6ae",  # Искусство
            ]
        }
    
    def generate_image(self, prompt: str, model_type: str = "nano") -> Tuple[str, int, str]:
        """Генерация изображения - возвращаем URL Unsplash"""
        logger.info(f"🎨 Demo görsel isteği: '{prompt[:50]}...'")
        
        if model_type not in self.prices:
            return "", 0, f"❌ Model desteklenmiyor"
        
        tokens_spent = self.prices[model_type]
        
        # Анализируем промпт для выбора категории
        prompt_lower = prompt.lower()
        category = "default"
        
        if any(word in prompt_lower for word in ["kadın", "kız", "bayan", "woman", "female", "kadın", "genç"]):
            category = "woman"
        elif any(word in prompt_lower for word in ["erkek", "adam", "man", "male"]):
            category = "man"
        elif any(word in prompt_lower for word in ["doğa", "manzara", "nature", "landscape", "orman", "dağ"]):
            category = "nature"
        elif any(word in prompt_lower for word in ["ev", "oda", "interior", "house", "iç", "dekor", "mobilya"]):
            category = "interior"
        elif any(word in prompt_lower for word in ["kedi", "cat", "köpek", "dog", "hayvan", "animal"]):
            # Животные
            image_url = "https://images.unsplash.com/photo-1514888286974-6d03bde4ba14?w=512&h=512&fit=crop"
            return image_url, tokens_spent, "Demo: Unsplash görseli"
        
        # Выбираем случайное изображение из категории
        if category in self.image_collection and self.image_collection[category]:
            image_url = random.choice(self.image_collection[category])
        else:
            image_url = random.choice(self.image_collection["default"])
        
        # Добавляем параметры для обрезки
        image_url = f"{image_url}?w=512&h=512&fit=crop&crop=faces"
        
        logger.info(f"✅ Demo görsel: {category} -> {image_url}")
        return image_url, tokens_spent, "Demo modu: Gerçek AI yakında!"
    
    def validate_api_key(self) -> bool:
        """Всегда True в демо-режиме"""
        return True

# Глобальный инстанс
image_gen = ImageGenerator()
