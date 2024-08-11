import time
import logging
from telebot import TeleBot, types
import re

# Установите уровень логирования
logging.basicConfig(level=logging.DEBUG)

# Создаем экземпляр бота
bot = TeleBot('7390214642:AAGVdkMdd4MPpzIrAaJн-x6fS8Utm7LZB4o', threaded=False)

# Словарь для хранения данных пользователей
user_dict = {}


class User:
    def __init__(self, name):
        self.name = name
        self.phone = None
        self.question = None


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        ask_question(message)
    else:
        markup = types.InlineKeyboardMarkup()
        bot_username = bot.get_me().username
        button = types.InlineKeyboardButton('Задать вопрос юристу', url=f't.me/{bot_username}?start=ask')
        markup.add(button)
        bot.send_message(message.chat.id, "Добро пожаловать! Нажмите кнопку ниже, чтобы задать вопрос юристу.",
                         reply_markup=markup)


# Обработчик команды /ask для личного чата
@bot.message_handler(func=lambda message: message.text.startswith('/start') or message.text == 'Задать вопрос юристу')
def handle_start(message):
    # Проверка, является ли это личным чатом
    if message.chat.type == 'private':
        ask_question(message)
    else:
        markup = types.InlineKeyboardMarkup()
        bot_username = bot.get_me().username
        button = types.InlineKeyboardButton('Задать вопрос юристу', url=f't.me/{bot_username}?start=ask')
        markup.add(button)
        bot.send_message(message.chat.id, "Пожалуйста, начните диалог со мной в личных сообщениях.",
                         reply_markup=markup)


# Функция для запроса вопроса
def ask_question(message):
    bot.send_message(message.chat.id,
                     'Задайте себе несколько вопросов:\n1. Решение моего вопроса облегчит мне жизнь?\n2. Я готов воспользоваться ответом юриста?\n3. Я готов решить данный вопрос окончательно?\nТолько, если на все вопросы ответ "Да", задавайте ваш вопрос.')
    question_msg = bot.send_message(message.chat.id, 'Напишите ваш вопрос:')
    bot.register_next_step_handler(question_msg, process_question_step)


# Обработчик шага ввода вопроса
def process_question_step(message):
    try:
        chat_id = message.chat.id
        question_text = message.text

        # Проверка на наличие букв в вопросе
        if not any(char.isalpha() for char in question_text):
            msg = bot.send_message(chat_id,
                                   'Вопрос не может состоять только из цифр. Пожалуйста, задайте вопрос, используя буквы.')
            bot.register_next_step_handler(msg, process_question_step)
            return

        user_dict[chat_id] = User(message.from_user.first_name)
        user = user_dict[chat_id]
        user.question = question_text
        phone_msg = bot.send_message(chat_id,
                                     'Для продолжения введите номер своего телефона в международном формате, пример: +79241233223')
        bot.register_next_step_handler(phone_msg, process_phone_step)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка. Попробуйте еще раз.')
        logging.error(f"Error in process_question_step: {e}")


# Обработчик шага ввода номера телефона
def process_phone_step(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if re.match(r"^\+\d{11}$", message.text):
        user.phone = message.text
        bot.send_message(chat_id, 'Спасибо! Ваш вопрос отправлен. С вами свяжутся юристы РО.')
        bot.send_message(-4273513647,
                         f'Новый вопрос от {message.from_user.first_name} @{message.from_user.username}\n\nВопрос: {user.question}\nКонтактный номер: {user.phone}')

        # Предлагаем задать новый вопрос
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button = types.KeyboardButton('Задать новый вопрос юристу')
        markup.add(button)
        bot.send_message(chat_id, 'Если у вас есть ещё вопросы, нажмите кнопку ниже.', reply_markup=markup)
    else:
        msg = bot.send_message(chat_id,
                               'Пожалуйста, введите корректный номер телефона в международном формате, пример: +79241233223.')
        bot.register_next_step_handler(msg, process_phone_step)


# Обработчик для кнопки "Задать новый вопрос юристу"
@bot.message_handler(func=lambda message: message.text == 'Задать новый вопрос юристу')
def new_question(message):
    ask_question(message)


# Функция для запуска бота с обработкой ошибок
def run_bot():
    while True:
        try:
            bot.polling(timeout=10, long_polling_timeout=30)
        except Exception as e:
            logging.error(f"Ошибка при запуске бота: {e}")
            time.sleep(1)  # Задержка перед повторной попыткой


if __name__ == "__main__":
    run_bot()
