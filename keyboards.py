def image_generation_menu():
    """Меню генерации изображений - ТОЛЬКО NANO BANANA"""
    keyboard = [
        [InlineKeyboardButton("🍌 Nano Banana", callback_data="image_nano")],
        [InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)
