import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = '7681923219:AAHAVieNBa9RbxcenAr9avg80-KXr6HneCw'

# Состояния для ConversationHandler
SELECTING_ACTION, ENTERING_ID, ENTERING_MESSAGE = range(3)

# База данных пользователей (ID: {name, telegram_id})
users_db = {
    "123": {"name": "Иван Иванов", "telegram_id": 654321},
    "456": {"name": "Петр Петров", "telegram_id": 987654},
    "789": {"name": "Сергей Сергеев", "telegram_id": 1427154863}
}


def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton('Пользователю')]],
        resize_keyboard=True
    )


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )
    return SELECTING_ACTION


async def select_action(update: Update, context: CallbackContext):
    text = update.message.text

    if text == 'Пользователю':
        # Формируем список пользователей
        users_list = "\n".join(
            [f"ID: {user_id} - {user_data['name']} (TG: {user_data['telegram_id']})"
             for user_id, user_data in users_db.items()]
        )

        await update.message.reply_text(
            f"Выберите кому хотите написать и напишите его ID:\n\n{users_list}",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Назад')]], resize_keyboard=True)
        )
        return ENTERING_ID

    await update.message.reply_text(
        "Пожалуйста, выберите один из вариантов:",
        reply_markup=get_main_keyboard()
    )
    return SELECTING_ACTION


async def enter_id(update: Update, context: CallbackContext):
    user_id = update.message.text

    if user_id == 'Назад':
        await update.message.reply_text(
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )
        return SELECTING_ACTION

    if user_id not in users_db:
        await update.message.reply_text(
            "Пользователь с таким ID не найден. Пожалуйста, введите корректный ID:"
        )
        return ENTERING_ID

    # Сохраняем данные получателя
    context.user_data['recipient'] = {
        'id': user_id,
        'name': users_db[user_id]['name'],
        'telegram_id': users_db[user_id]['telegram_id']
    }

    await update.message.reply_text(
        f"Введите вопрос пользователю {users_db[user_id]['name']} (ID: {user_id}):",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Отмена')]], resize_keyboard=True)
    )
    return ENTERING_MESSAGE


async def enter_message(update: Update, context: CallbackContext):
    message_text = update.message.text
    sender_id = "456"  #TODO: заменить на системный

    if message_text == 'Отмена':
        await update.message.reply_text("Действие отменено.", reply_markup=get_main_keyboard())
        return SELECTING_ACTION

    recipient = context.user_data['recipient']

    # Сообщение для отправителя
    sender_message = f"""📨 Сообщение для: {recipient['name']} (ID: {recipient['id']})
От отправителя: {sender_id}
----------------------------
{message_text}
----------------------------"""

    await update.message.reply_text(sender_message, reply_markup=get_main_keyboard())

    recipient_message = f"""📨 Вам новое сообщение от пользователя с ID: {sender_id}
----------------------------
{message_text}
----------------------------"""

    try:
        await context.bot.send_message(
            chat_id=recipient['telegram_id'],
            text=recipient_message
        )
        logger.info(f"Сообщение отправлено пользователю {recipient['telegram_id']}")
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        await update.message.reply_text(
            "❌ Не удалось отправить сообщение получателю",
            reply_markup=get_main_keyboard()
        )

    return SELECTING_ACTION


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Действие отменено.",
        reply_markup=get_main_keyboard()
    )
    return SELECTING_ACTION


async def test(update: Update, context: CallbackContext):
    """Тестовая команда для проверки отправки сообщений"""
    try:
        await context.bot.send_message(
            chat_id=1427154863,  # Ваш Telegram ID
            text="✅ Это тестовое сообщение от бота"
        )
        await update.message.reply_text("Тестовое сообщение отправлено!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_action)
            ],
            ENTERING_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_id)
            ],
            ENTERING_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_message)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('test', test))  # Добавляем тестовую команду

    logger.info("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()
