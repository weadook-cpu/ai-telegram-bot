# В image_generator.py добавить:
from gemini_generator import gemini_gen

class ImageGenerator:
    def generate_image(self, prompt: str, model_type: str = "nano") -> Tuple[str, int, str]:
        # Используем Gemini для улучшения промпта
        if gemini_gen.is_available():
            enhanced_prompt = gemini_gen.generate_image_prompt(prompt)
            logger.info(f"🔄 Geliştirilmiş prompt: {enhanced_prompt[:100]}...")
        else:
            enhanced_prompt = prompt
        
        # Дальше обычная логика с Unsplash...
