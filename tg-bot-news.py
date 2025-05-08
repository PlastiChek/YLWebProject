import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes
from telegram.ext import filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '7852977293:AAErYW-USOtu5Y_4PsMg-caKta23sofD9Ww'
ADMIN_ID = 1427154863

subscribed_users = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    subscribed_users.add(user.id)
    logger.info(f"New subscriber: {user.id}")

    # Сообщение видно только пользователю
    await update.message.reply_text(
        "Вы подписались на новостную рассылку!\n"
        "Теперь вы будете получать все обновления от администратора."
    )

    # Уведомление админа (только если это не он сам)
    if user.id != ADMIN_ID:
        try:
            await context.bot.send_message(
                ADMIN_ID,
                f"➕ Новый подписчик: {user.full_name} (ID: {user.id})\n"
                f"Всего подписчиков: {len(subscribed_users)}"
            )
        except Exception as e:
            logger.error(f"Can't notify admin: {e}")


async def admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка сообщений от админа для рассылки."""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав администратора.")
        return

    message = update.message
    success_count = 0
    fail_count = 0
    errors = []

    # Рассылка всем подписчикам
    for user_id in subscribed_users:
        try:
            await message.copy(user_id)
            success_count += 1
        except Exception as e:
            fail_count += 1
            errors.append(f"{user_id}: {str(e)}")
            logger.error(f"Send failed to {user_id}: {e}")

    # Формируем отчет для админа
    report = (
        f"Отчет о рассылке:\n"
        f"• Получили: {success_count}\n"
        f"• Не доставлено: {fail_count}\n"
        f"• Всего подписчиков: {len(subscribed_users)}"
    )

    # Если были ошибки, добавляем их в отчет
    if errors:
        report += "\n\nОшибки:\n" + "\n".join(errors[:5])  # Показываем первые 5 ошибок

    # Отправляем отчет админу
    await context.bot.send_message(ADMIN_ID, report)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /stats для админа - статистика подписчиков."""
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(
            f"Статистика:\n"
            f"Всего подписчиков: {len(subscribed_users)}\n"
            f"ID подписчиков: {list(subscribed_users)[:10]}"  # Показываем первые 10 ID
        )


def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))

    # Обработчик сообщений от админа
    application.add_handler(MessageHandler(
        filters.Chat(ADMIN_ID) & ~filters.COMMAND,
        admin_message
    ))

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    main()
