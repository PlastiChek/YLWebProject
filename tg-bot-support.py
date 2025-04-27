import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Настройка логирования только в консоль
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = '7681923219:AAHAVieNBa9RbxcenAr9avg80-KXr6HneCw'


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


async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.effective_user

    responses = {
        'Продавцу': "Вы выбрали связь с продавцом. Опишите ваш вопрос.",
        'Покупателю': "Вы выбрали связь с покупателем. Чем можем помочь?",
        'Админу': "Обращение к администратору. Опишите проблему."
    }

    if text in responses:
        logger.info(f"User {user.id} selected: {text}")
        await update.message.reply_text(responses[text])
    else:
        logger.info(f"User {user.id} sent message: {text}")
        await update.message.reply_text(
            "Пожалуйста, выберите один из вариантов:",
            reply_markup=get_keyboard()
        )


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting bot...")
    application.run_polling()


if __name__ == '__main__':
    main()