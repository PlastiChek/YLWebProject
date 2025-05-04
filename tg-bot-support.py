import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# Настройка логирования только в консоль
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = '7681923219:AAHAVieNBa9RbxcenAr9avg80-KXr6HneCw'

# Состояния для ConversationHandler
SELECTING_ACTION, ENTERING_ID, ENTERING_MESSAGE = range(3)


def get_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton('Продавцу')],
            [KeyboardButton('Покупателю')],
            [KeyboardButton('Админу')]
        ],
        resize_keyboard=True
    )


async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")
    await update.message.reply_text(
        "Выберите, кому хотите написать:",
        reply_markup=get_keyboard()
    )
    return SELECTING_ACTION


async def select_action(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.effective_user

    if text in ['Продавцу', 'Покупателю']:
        context.user_data['recipient_type'] = text.lower()
        logger.info(f"User {user.id} selected: {text}")
        await update.message.reply_text(f"Вы выбрали связь с {text.lower()}. Пожалуйста, введите ID:")
        return ENTERING_ID
    elif text == 'Админу':
        logger.info(f"User {user.id} selected: Админу")
        await update.message.reply_text("Обращение к администратору. Опишите проблему:")
        return ENTERING_MESSAGE
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите один из вариантов:",
            reply_markup=get_keyboard()
        )
        return SELECTING_ACTION


async def enter_id(update: Update, context: CallbackContext):
    user_id = update.message.text
    context.user_data['recipient_id'] = user_id
    recipient_type = context.user_data['recipient_type']

    logger.info(f"User {update.effective_user.id} entered ID: {user_id} for {recipient_type}")
    await update.message.reply_text(f"ID {recipient_type} сохранен. Теперь напишите ваш вопрос:")
    return ENTERING_MESSAGE


async def enter_message(update: Update, context: CallbackContext):
    message_text = update.message.text
    user = update.effective_user
    recipient_type = context.user_data.get('recipient_type', 'админу')

    if 'recipient_id' in context.user_data:
        recipient_id = context.user_data['recipient_id']
        logger.info(f"Message to {recipient_type} (ID: {recipient_id}) from user {user.id}: {message_text}")
        await update.message.reply_text(f"Ваше сообщение для {recipient_type} (ID: {recipient_id}) отправлено!")
    else:
        logger.info(f"Message to admin from user {user.id}: {message_text}")
        await update.message.reply_text("Ваше сообщение администратору отправлено!")

    await update.message.reply_text(
        "Выберите, кому хотите написать:",
        reply_markup=get_keyboard()
    )
    return SELECTING_ACTION


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Действие отменено. Выберите, кому хотите написать:",
        reply_markup=get_keyboard()
    )
    return SELECTING_ACTION


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
    logger.info("Starting bot...")
    application.run_polling()


if __name__ == '__main__':
    main()
