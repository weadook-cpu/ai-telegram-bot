# image_generator.py - ПРОСТОЙ РАБОЧИЙ ВАРИАНТ
import logging
import random
import hashlib
from typing import Tuple

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Простой генератор изображений - только демо"""
    
    def __init__(self):
        self.prices = {"nano": 100}
        logger.info("✅ Basit görsel jeneratör başlatıldı")
    
    def generate_image(self, prompt: str, model_type: str = "nano") -> Tuple[str, int, str]:
        """Простая генерация - всегда разные изображения"""
        logger.info(f"🎨 Görsel isteği: '{prompt[:30]}...'")
        
        # Список хороших Unsplash фото (разные категории)
        unsplash_urls = [
            # Женщины
            "https://images.unsplash.com/photo-1494790108755-2616b612b786",
            "https://images.unsplash.com/photo-1534528741775-53994a69daeb",
            "https://images.unsplash.com/photo-1517841905240-472988babdf9",
            
            # Мужчины
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
            "https://images.unsplash.com/photo-1500648767791-00dcc994a43e",
            
            # Природа
            "https://images.unsplash.com/photo-1501854140801-50d01698950b",
            "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05",
            
            # Море/Пляж
            "https://images.unsplash.com/photo-1439066615861-d1af74d74000",
            "https://images.unsplash.com/photo-1475924156734-496f6cac6ec1",
            
            # Животные
            "https://images.unsplash.com/photo-1514888286974-6d03bde4ba14",
            "https://images.unsplash.com/photo-1516371535707-512a1e83bb9a",
            
            # Города
            "https://images.unsplash.com/photo-1449824913935-59a10b8d2000",
            "https://images.unsplash.com/photo-1545048702-79362596cdc9",
            
            # Еда
            "https://images.unsplash.com/photo-1565958011703-44f9829ba187",
            "https://images.unsplash.com/photo-1482049016688-2d3e1b311543",
        ]
        
        # Выбираем случайное изображение
        image_url = random.choice(unsplash_urls)
        
        # Добавляем параметры для обрезки
        image_url = f"{image_url}?w=512&h=512&fit=crop"
        
        logger.info(f"✅ Görsel gönderiliyor: {image_url[:60]}...")
        return image_url, 100, "Demo modu: Gerçek AI yakında!"
    
    def validate_api_key(self) -> bool:
        return True

# Глобальный инстанс
image_gen = ImageGenerator()
