# Вместо этого:
# await update.message.reply_photo(
#     photo=image_url,

# Используй это:
if os.path.exists(image_url):  # Если это локальный файл
    with open(image_url, 'rb') as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=f"🎨 <b>{model_name}</b>\n\n"
                   f"📝 <b>Prompt:</b> {prompt}\n"
                   f"🪙 <b>Token:</b> {tokens_spent}\n"
                   f"💰 <b>Kalan bakiye:</b> {db.get_user_tokens(user_id)}",
            parse_mode="HTML",
            reply_markup=back_button()
        )
    # Удаляем временный файл
    try:
        os.remove(image_url)
    except:
        pass
else:
    # Если это URL
    await update.message.reply_photo(
        photo=image_url,
        caption=f"🎨 <b>{model_name}</b>\n\n"
               f"📝 <b>Prompt:</b> {prompt}\n"
               f"🪙 <b>Token:</b> {tokens_spent}\n"
               f"💰 <b>Kalan bakiye:</b> {db.get_user_tokens(user_id)}",
        parse_mode="HTML",
        reply_markup=back_button()
    )
