import re
import logging
from telebot import types

from user_manager import User, UserManager
import config

user_manager = UserManager()


def start_handler(bot, message):
    if message.chat.type == 'private':
        ask_question(bot, message)
    else:
        markup = types.InlineKeyboardMarkup()
        bot_username = bot.get_me().username
        button = types.InlineKeyboardButton('Задать вопрос юристу', url=f't.me/{bot_username}?start=ask')
        markup.add(button)
        bot.send_message(
            message.chat.id,
            "Добро пожаловать! Нажмите кнопку ниже, чтобы задать вопрос юристу.",
            reply_markup=markup
        )


def ask_question(bot, message):
    bot.send_message(
        message.chat.id,
        'Задайте себе несколько вопросов:\n'
        '1. Решение моего вопроса облегчит мне жизнь?\n'
        '2. Я готов воспользоваться ответом юриста?\n'
        '3. Я готов решить данный вопрос окончательно?\n'
        'Только, если на все вопросы ответ "Да", задавайте ваш вопрос.'
    )
    question_msg = bot.send_message(message.chat.id, 'Напишите ваш вопрос:')
    bot.register_next_step_handler(question_msg, lambda msg: process_question_step(bot, msg))


def process_question_step(bot, message):
    try:
        chat_id = message.chat.id
        question_text = message.text

        # Проверка на наличие букв в вопросе
        if not any(char.isalpha() for char in question_text):
            msg = bot.send_message(
                chat_id,
               'Вопрос не может состоять только из цифр. Пожалуйста, задайте вопрос, используя буквы.'
            )
            bot.register_next_step_handler(msg, lambda msg: process_question_step(bot, msg))
            return

        user = User(message.from_user.first_name)
        user.question = question_text
        user_manager.add_user(chat_id, user)

        phone_msg = bot.send_message(
            chat_id,
            'Для продолжения введите номер своего телефона в международном формате, пример: +79241233223'
        )
        bot.register_next_step_handler(phone_msg, lambda msg: process_phone_step(bot, msg))
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка. Попробуйте еще раз.')
        logging.error(f"Error in process_question_step: {e}")


def process_phone_step(bot, message):
    chat_id = message.chat.id
    user = user_manager.get_user(chat_id)
    if re.match(r"^\+\d{11}$", message.text):
        user.phone = message.text
        bot.send_message(chat_id, 'Спасибо! Ваш вопрос отправлен. С вами свяжутся юристы РО.')
        bot.send_message(
            config.LAWYER_CHAT_ID,
            f'Новый вопрос от {message.from_user.first_name} @{message.from_user.username}\n\n'
            f'Вопрос: {user.question}\nКонтактный номер: {user.phone}')

        # Предлагаем задать новый вопрос
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button = types.KeyboardButton('Задать новый вопрос юристу')
        markup.add(button)
        bot.send_message(
            chat_id,
            'Если у вас есть ещё вопросы, нажмите кнопку ниже.', reply_markup=markup
        )
    else:
        msg = bot.send_message(
            chat_id,
           'Пожалуйста, введите корректный номер телефона в международном формате, пример: +79241233223.'
        )
        bot.register_next_step_handler(msg, lambda msg: process_phone_step(bot, msg))


def new_question_handler(bot, message):
    ask_question(bot, message)
