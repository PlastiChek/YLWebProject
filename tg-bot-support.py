import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ConversationHandler,
)
import sqlite3

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7681923219:AAHAVieNBa9RbxcenAr9avg80-KXr6HneCw"

# Состояния для ConversationHandler
SELECTING_ACTION, ENTERING_ID, ENTERING_MESSAGE, ADMIN_MESSAGE = range(4)

# Функция для загрузки пользователей из БД
def load_users_from_db():
    users = {}
    try:
        conn = sqlite3.connect("db/shops.sqlite")  # Путь к вашей БД
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, telegram_id FROM users")

        for row in cursor.fetchall():
            user_id, name, telegram_id = row
            users[str(user_id)] = {
                "name": name if name else "Не указано",
                "telegram_id": telegram_id if telegram_id else None,
            }

        conn.close()
    except Exception as e:
        logger.error(f"Ошибка загрузки пользователей из БД: {e}")
        # Тестовые данные, если БД недоступна
        users = {
            "1": {"name": "Иван Иванов", "telegram_id": 654321},
            "2": {"name": "Петр Петров", "telegram_id": 987654},
            "3": {"name": "Сергей Сергеев", "telegram_id": 1427154863},
        }
    return users

# Загружаем пользователей при старте
users_db = load_users_from_db()

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("Пользователю")],
            [KeyboardButton("Админу")],  # Новая кнопка
        ],
        resize_keyboard=True,
    )

async def start(update: Update, context: CallbackContext):
    # Сохраняем chat_id пользователя, который запустил бота
    context.user_data["bot_starter_chat_id"] = update.message.chat_id
    await update.message.reply_text(
        "Выберите действие:", reply_markup=get_main_keyboard()
    )
    return SELECTING_ACTION

async def select_action(update: Update, context: CallbackContext):
    text = update.message.text

    if text == "Пользователю":
        # Формируем список пользователей
        users_list = "\n".join(
            [
                f"ID: {user_id} - {user_data['name']} (TG: {user_data['telegram_id'] or 'не указан'})"
                for user_id, user_data in users_db.items()
            ]
        )

        await update.message.reply_text(
            f"Выберите кому хотите написать и напишите его ID:\n\n{users_list}",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("Назад")]], resize_keyboard=True
            ),
        )
        return ENTERING_ID

    elif text == "Админу":
        await update.message.reply_text(
            "Введите сообщение для админа:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("Отмена")]], resize_keyboard=True
            ),
        )
        return ADMIN_MESSAGE

    await update.message.reply_text(
        "Пожалуйста, выберите один из вариантов:", reply_markup=get_main_keyboard()
    )
    return SELECTING_ACTION

async def enter_id(update: Update, context: CallbackContext):
    user_id = update.message.text

    if user_id == "Назад":
        await update.message.reply_text(
            "Выберите действие:", reply_markup=get_main_keyboard()
        )
        return SELECTING_ACTION

    if user_id not in users_db:
        await update.message.reply_text(
            "Пользователь с таким ID не найден. Пожалуйста, введите корректный ID:"
        )
        return ENTERING_ID

    if not users_db[user_id]["telegram_id"]:
        await update.message.reply_text(
            f"У пользователя {users_db[user_id]['name']} не указан Telegram ID. Сообщение не может быть отправлено.",
            reply_markup=get_main_keyboard(),
        )
        return SELECTING_ACTION

    # Сохраняем данные получателя
    context.user_data["recipient"] = {
        "id": user_id,
        "name": users_db[user_id]["name"],
        "telegram_id": users_db[user_id]["telegram_id"],
    }

    await update.message.reply_text(
        f"Введите вопрос пользователю {users_db[user_id]['name']} (ID: {user_id}):",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Отмена")]], resize_keyboard=True
        ),
    )
    return ENTERING_MESSAGE

async def enter_message(update: Update, context: CallbackContext):
    message_text = update.message.text
    sender_id = str(update.message.from_user.id)

    if message_text == "Отмена":
        await update.message.reply_text(
            "Действие отменено.", reply_markup=get_main_keyboard()
        )
        return SELECTING_ACTION

    recipient = context.user_data["recipient"]

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
            chat_id=recipient["telegram_id"], text=recipient_message
        )
        logger.info(f"Сообщение отправлено пользователю {recipient['telegram_id']}")
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        await update.message.reply_text(
            "❌ Не удалось отправить сообщение получателю", reply_markup=get_main_keyboard()
        )

    return SELECTING_ACTION

async def handle_admin_message(update: Update, context: CallbackContext):
    message_text = update.message.text

    if message_text == "Отмена":
        await update.message.reply_text(
            "Действие отменено.", reply_markup=get_main_keyboard()
        )
        return SELECTING_ACTION

    # Получаем chat_id пользователя, который запустил бота
    recipient_chat_id = context.user_data.get("bot_starter_chat_id")

    if not recipient_chat_id:
        await update.message.reply_text(
            "❌ Не удалось определить получателя", reply_markup=get_main_keyboard()
        )
        return SELECTING_ACTION

    # Сообщение для отправителя (админа)
    await update.message.reply_text(
        f"""📨 Сообщение отправлено админу:
----------------------------
{message_text}
----------------------------""",
        reply_markup=get_main_keyboard(),
    )

    # Сообщение для получателя (с пометкой "от админа")
    try:
        await context.bot.send_message(
            chat_id=recipient_chat_id,
            text=f"""📨 Вам сообщение от админа:
----------------------------
{message_text}
----------------------------""",
        )
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        await update.message.reply_text(
            "❌ Не удалось отправить сообщение", reply_markup=get_main_keyboard()
        )

    return SELECTING_ACTION

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Действие отменено.", reply_markup=get_main_keyboard()
    )
    return SELECTING_ACTION

async def reload_users(update: Update, context: CallbackContext):
    """Команда для перезагрузки пользователей из БД"""
    global users_db
    users_db = load_users_from_db()
    await update.message.reply_text(
        f"База пользователей перезагружена. Загружено {len(users_db)} пользователей."
    )

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_action)
            ],
            ENTERING_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_id)
            ],
            ENTERING_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_message)
            ],
            ADMIN_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("reload", reload_users))

    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()