# gemini_generator.py
import os
import logging
import google.generativeai as genai
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class GeminiGenerator:
    """Реальная генерация через Gemini API"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("❌ GEMINI_API_KEY bulunamadı!")
            self.available = False
            return
            
        try:
            genai.configure(api_key=self.api_key)
            # Gemini 1.5 Pro поддерживает генерацию изображений?
            # Пока Gemini не генерирует изображения напрямую
            # Но может создавать описания для других API
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.available = True
            logger.info("✅ Gemini API başlatıldı")
        except Exception as e:
            logger.error(f"❌ Gemini hatası: {e}")
            self.available = False
    
    def generate_image_prompt(self, user_prompt: str) -> str:
        """Создать детальный промпт для генерации изображения"""
        if not self.available:
            return user_prompt
        
        try:
            system_prompt = """
            Sen bir görsel oluşturma asistanısın. Kullanıcının basit açıklamasını 
            detaylı, görsel oluşturucular için optimize edilmiş bir prompt'a dönüştür.
            
            Format:
            1. Ana konu (Türkçe)
            2. Stil (fotoğraf, dijital sanat, yağlı boya, vs.)
            3. Renk paleti
            4. Işık ve atmosfer
            5. Ek detaylar
            
            Örnek:
            Kullanıcı: "deniz manzarası"
            Sen: "Akdeniz'de gün batımı, turkuaz deniz, altın rengi gökyüzü, 
            kumsal, palmiye ağaçları, sıcak renkler, foto-gerçekçi, 8K kalite, 
            profesyonel fotoğrafçılık, doğal ışık, huzurlu atmosfer"
            """
            
            response = self.model.generate_content(
                f"{system_prompt}\n\nKullanıcı: {user_prompt}\n\nDetaylı prompt:"
            )
            
            detailed_prompt = response.text.strip()
            logger.info(f"✅ Gemini prompt: {detailed_prompt[:100]}...")
            return detailed_prompt
            
        except Exception as e:
            logger.error(f"❌ Gemini prompt hatası: {e}")
            return user_prompt
    
    def is_available(self) -> bool:
        return self.available

# Глобальный инстанс
gemini_gen = GeminiGenerator()
