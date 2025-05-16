import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '7852977293:AAErYW-USOtu5Y_4PsMg-caKta23sofD9Ww'
ADMIN_ID = 1427154863

subscribed_users = set()


# Клавиатуры
def get_user_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📩 Подписаться"), KeyboardButton("🚫 Отписаться")],
        [KeyboardButton("ℹ️ Помощь")]
    ], resize_keyboard=True)


def get_admin_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📢 Сделать рассылку")],
        [KeyboardButton("📊 Статистика"), KeyboardButton("📝 Экспорт подписчиков")],
        [KeyboardButton("👤 Обычный режим")]
    ], resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "👑 Вы вошли как администратор",
            reply_markup=get_admin_keyboard()
        )
    else:
        await update.message.reply_text(
            "Добро пожаловать! Используйте кнопки ниже:",
            reply_markup=get_user_keyboard()
        )


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    user = update.effective_user
    text = update.message.text if update.message.text else ""

    if user.id == ADMIN_ID:
        if text == "📢 Сделать рассылку":
            await update.message.reply_text(
                "Отправьте сообщение для рассылки (текст, фото или документ):",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Отмена")]], resize_keyboard=True)
            )
            context.user_data['awaiting_message'] = True
            return

        elif text == "📊 Статистика":
            await stats(update, context)
            return

        elif text == "📝 Экспорт подписчиков":
            await export_users(update, context)
            return

        elif text == "👤 Обычный режим":
            await update.message.reply_text(
                "Переключено в обычный режим",
                reply_markup=get_user_keyboard()
            )
            return

        elif text == "❌ Отмена":
            await update.message.reply_text(
                "Рассылка отменена",
                reply_markup=get_admin_keyboard()
            )
            context.user_data.pop('awaiting_message', None)
            return

        elif context.user_data.get('awaiting_message'):
            await admin_message(update, context)
            return

    if text == "📩 Подписаться":
        await subscribe(update, context)
    elif text == "🚫 Отписаться":
        await unsubscribe(update, context)
    elif text == "ℹ️ Помощь":
        await help_command(update, context)


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    if user.id in subscribed_users:
        await update.message.reply_text("Вы уже подписаны!")
        return

    subscribed_users.add(user.id)
    logger.info(f"New subscriber: {user.id}")

    await update.message.reply_text(
        "✅ Вы успешно подписались на рассылку!",
        reply_markup=get_user_keyboard()
    )

    try:
        await context.bot.send_message(
            ADMIN_ID,
            f"➕ Новый подписчик: {user.full_name} (ID: {user.id})\n"
            f"Всего подписчиков: {len(subscribed_users)}"
        )
    except Exception as e:
        logger.error(f"Can't notify admin: {e}")


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    if user.id not in subscribed_users:
        await update.message.reply_text("Вы не подписаны!")
        return

    subscribed_users.remove(user.id)
    logger.info(f"User {user.id} unsubscribed")

    await update.message.reply_text(
        "🔕 Вы отписались от рассылки.",
        reply_markup=get_user_keyboard()
    )

    try:
        await context.bot.send_message(
            ADMIN_ID,
            f"➖ Отписался: {user.full_name} (ID: {user.id})\n"
            f"Осталось подписчиков: {len(subscribed_users)}"
        )
    except Exception as e:
        logger.error(f"Can't notify admin: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "ℹ️ <b>Информация о боте</b>\n\n"
        "Это новостной бот для рассылки обновлений.\n"
        "Используйте кнопки для управления подпиской:\n\n"
        "📩 <b>Подписаться</b> - получать рассылку\n"
        "🚫 <b>Отписаться</b> - перестать получать сообщения\n\n"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)


async def admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Рассылка сообщения всем подписчикам"""
    message = update.message
    success_count = 0
    fail_count = 0
    errors = []

    # Определяем тип контента
    content_type = None
    if message.text:
        content_type = "text"
    elif message.photo:
        content_type = "photo"
    elif message.document:
        content_type = "document"

    for user_id in subscribed_users:
        try:
            if content_type == "text":
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message.text
                )
            elif content_type == "photo":
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption
                )
            elif content_type == "document":
                await context.bot.send_document(
                    chat_id=user_id,
                    document=message.document.file_id,
                    caption=message.caption
                )
            success_count += 1
        except Exception as e:
            fail_count += 1
            errors.append(f"{user_id}: {str(e)}")
            logger.error(f"Send failed to {user_id}: {e}")

    report = (
        f"📊 <b>Отчет о рассылке</b>\n\n"
        f"📤 Тип: <b>{content_type}</b>\n"
        f"✅ Получили: <b>{success_count}</b>\n"
        f"❌ Не доставлено: <b>{fail_count}</b>\n"
        f"👥 Всего подписчиков: <b>{len(subscribed_users)}</b>"
    )

    if errors:
        report += "\n\n<b>Ошибки:</b>\n" + "\n".join(errors[:3])

    await context.bot.send_message(
        ADMIN_ID,
        report,
        parse_mode=ParseMode.HTML,
        reply_markup=get_admin_keyboard()
    )

    context.user_data.pop('awaiting_message', None)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stats_text = (
        f"📈 <b>Статистика</b>\n\n"
        f"👥 Всего подписчиков: <b>{len(subscribed_users)}</b>\n"
        f"📝 Последние 5 ID:\n{', '.join(map(str, list(subscribed_users)[:5]))}"
    )

    await update.message.reply_text(
        stats_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_admin_keyboard()
    )


async def export_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not subscribed_users:
        await update.message.reply_text("Нет подписчиков для экспорта")
        return

    users_list = "\n".join([f"{i + 1}. {uid}" for i, uid in enumerate(subscribed_users)])
    await update.message.reply_text(
        f"📝 Список подписчиков ({len(subscribed_users)}):\n\n{users_list}",
        reply_markup=get_admin_keyboard()
    )


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    # Универсальный обработчик для всех типов сообщений от админа
    application.add_handler(MessageHandler(
        filters.Chat(ADMIN_ID) & (
                filters.TEXT |
                filters.PHOTO |
                filters.ATTACHMENT
        ),
        admin_message
    ))
    logger.info("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()
