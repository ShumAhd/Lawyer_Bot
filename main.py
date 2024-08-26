import time
import logging
from telebot import TeleBot
from handlers import start_handler, new_question_handler
import config

# Установите уровень логирования
logging.basicConfig(level=logging.WARNING)

# Создаем экземпляр бота
bot = TeleBot(config.TOKEN, threaded=False)


# Привязка обработчиков команд
@bot.message_handler(commands=['start'])
def handle_start(message):
    start_handler(bot, message)


@bot.message_handler(func=lambda message: message.text == 'Задать новый вопрос юристу')
def handle_new_question(message):
    new_question_handler(bot, message)


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
