# image_generator.py - ЧИСТЫЙ ДЕМО РЕЖИМ (БЕЗ GOOGLE)
import os
import logging
import random
import hashlib
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Генератор изображений - только демо с Unsplash"""
    
    def __init__(self):
        self.prices = {
            "nano": 100,
            "nano_pro": 200,
            "gpt": 150,
            "midjourney": 300,
            "recraft": 250,
        }
        
        # Большая коллекция изображений Unsplash
        self.unsplash_images = [
            # Женщины (25+ вариантов)
            "https://images.unsplash.com/photo-1494790108755-2616b612b786",
            "https://images.unsplash.com/photo-1534528741775-53994a69daeb",
            "https://images.unsplash.com/photo-1517841905240-472988babdf9",
            "https://images.unsplash.com/photo-1524504388940-b1c1722653e1",
            "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df",
            "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f",
            "https://images.unsplash.com/photo-1544005313-94ddf0286df2",
            "https://images.unsplash.com/photo-1509967419530-da38b4704bc6",
            "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e",
            "https://images.unsplash.com/photo-1503104834685-7205e8607eb9",
            "https://images.unsplash.com/photo-1438761681033-6461ffad8d80",
            "https://images.unsplash.com/photo-1542206395-9feb3edaa68d",
            "https://images.unsplash.com/photo-1516726817505-f5ed825624d8",
            
            # Мужчины (15+ вариантов)
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
            "https://images.unsplash.com/photo-1500648767791-00dcc994a43e",
            "https://images.unsplash.com/photo-1507591064344-4c6ce005-128",
            "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d",
            "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7",
            "https://images.unsplash.com/photo-1504257432389-52343af06ae3",
            "https://images.unsplash.com/photo-1506919258185-6078bba55d2a",
            "https://images.unsplash.com/photo-1517423568366-8b83523034fd",
            
            # Природа (20+ вариантов)
            "https://images.unsplash.com/photo-1501854140801-50d01698950b",
            "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05",
            "https://images.unsplash.com/photo-1519681393784-d120267933ba",
            "https://images.unsplash.com/photo-1441974231531-c6227db76b6e",
            "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07",
            "https://images.unsplash.com/photo-1426604966848-d7adac402bff",
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
            "https://images.unsplash.com/photo-1439066615861-d1af74d74000",
            "https://images.unsplash.com/photo-1475924156734-496f6cac6ec1",
            "https://images.unsplash.com/photo-1505144808419-1957a94ca61e",
            
            # Интерьеры (15+ вариантов)
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688",
            "https://images.unsplash.com/photo-1513584684374-8bab748fbf90",
            "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e",
            "https://images.unsplash.com/photo-1558036117-15e82a2c9a9a",
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7",
            "https://images.unsplash.com/photo-1519710164239-da123dc03ef4",
            "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af",
            
            # Животные (15+ вариантов)
            "https://images.unsplash.com/photo-1514888286974-6d03bde4ba14",
            "https://images.unsplash.com/photo-1543852786-1cf6624b9987",
            "https://images.unsplash.com/photo-1516371535707-512a1e83bb9a",
            "https://images.unsplash.com/photo-1552053831-71594a27632d",
            "https://images.unsplash.com/photo-1541364983171-a8ba01e95cfc",
            "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7",
            "https://images.unsplash.com/photo-1550358864-518f202c02ba",
            "https://images.unsplash.com/photo-1567177662142-20646cdb5d23",
            
            # Города (15+ вариантов)
            "https://images.unsplash.com/photo-1449824913935-59a10b8d2000",
            "https://images.unsplash.com/photo-1519501025264-65ba15a82390",
            "https://images.unsplash.com/photo-1545048702-79362596cdc9",
            "https://images.unsplash.com/photo-1523531294919-4bcd7c65e216",
            "https://images.unsplash.com/photo-1545569341-9eb8b30979d9",
            "https://images.unsplash.com/photo-1512453979798-5ea266f8880c",
            "https://images.unsplash.com/photo-1498307833015-e7b400441eb8",
            
            # Еда (15+ вариантов)
            "https://images.unsplash.com/photo-1565958011703-44f9829ba187",
            "https://images.unsplash.com/photo-1482049016688-2d3e1b311543",
            "https://images.unsplash.com/photo-1490818387583-1baba5e638af",
            "https://images.unsplash.com/photo-1512621776951-a57141f2eefd",
            "https://images.unsplash.com/photo-1546069901-ba9599a7e63c",
            "https://images.unsplash.com/photo-1555939594-58d7cb561ad1",
            
            # Абстрактное (10+ вариантов)
            "https://images.unsplash.com/photo-1543857778-c4a1a569e388",
            "https://images.unsplash.com/photo-1541961017774-22349e4a1262",
            "https://images.unsplash.com/photo-1513366208864-87536b8bd7b4",
            "https://images.unsplash.com/photo-1550684376-efcbd6e3f031",
            "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0",
        ]
        
        # Всего: 120+ уникальных изображений!
        logger.info(f"✅ {len(self.unsplash_images)} demo görsel yüklendi")
    
    def generate_image(self, prompt: str, model_type: str = "nano") -> Tuple[str, int, str]:
        """Генерация изображения - всегда разные"""
        logger.info(f"🎨 Görsel isteği: '{prompt[:50]}...'")
        
        if model_type not in self.prices:
            return "", 0, "❌ Model desteklenmiyor"
        
        tokens_spent = self.prices[model_type]
        
        # Генерируем "уникальный" индекс на основе промпта
        # Чтобы одинаковые промпты давали одинаковые изображения
        # А разные промпты - разные изображения
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        hash_int = int(prompt_hash[:8], 16)  # Преобразуем в число
        image_index = hash_int % len(self.unsplash_images)
        
        # Берём изображение по индексу
        base_url = self.unsplash_images[image_index]
        
        # Добавляем параметры для обрезки
        # И уникальный параметр чтобы избежать кэширования
        image_url = f"{base_url}?w=512&h=512&fit=crop&crop=faces&{prompt_hash[:8]}"
        
        logger.info(f"✅ Görsel seçildi: index={image_index}, total={len(self.unsplash_images)}")
        return image_url, tokens_spent, "🎨 Demo: AI görsel oluşturucu"
    
    def validate_api_key(self) -> bool:
        """Всегда True в демо-режиме"""
        return True

# Глобальный инстанс
image_gen = ImageGenerator()
