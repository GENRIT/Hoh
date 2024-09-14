import telebot
from playwright.sync_api import sync_playwright
import os

# Токен вашего телеграм-бота
API_TOKEN = '7332817569:AAG3l2IJugs0geomZCaT9k-YoVcwBXcHAgs'

# Создаем экземпляр бота
bot = telebot.TeleBot(API_TOKEN)

# Функция для создания скриншота сайта
def take_screenshot(url):
    screenshot_path = "screenshot.png"
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)  # Запускаем браузер в headless режиме (без графического интерфейса)
            page = browser.new_page()
            print(f"Открываю страницу: {url}")
            page.goto(url)
            page.wait_for_load_state("networkidle")  # Ждем, пока загрузка страницы завершится
            print(f"Создаю скриншот и сохраняю как: {screenshot_path}")
            page.screenshot(path=screenshot_path)
            browser.close()  # Закрываем браузер
            print("Браузер успешно закрыт.")
        # Проверяем, что файл скриншота был создан
        if not os.path.exists(screenshot_path):
            raise Exception("Скриншот не был сохранен.")
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        screenshot_path = None
    return screenshot_path

# Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку, и я сделаю скриншот сайта.")

# Обрабатываем все текстовые сообщения
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if url.startswith("http://") or url.startswith("https://"):
        bot.reply_to(message, "Подожди, делаю скриншот сайта...")
        screenshot = take_screenshot(url)
        if screenshot:
            try:
                with open(screenshot, 'rb') as screenshot_file:
                    bot.send_photo(message.chat.id, screenshot_file)
            except Exception as e:
                bot.reply_to(message, f"Не удалось отправить скриншот: {e}")
        else:
            bot.reply_to(message, "Не удалось сделать скриншот. Попробуйте еще раз.")
    else:
        bot.reply_to(message, "Пожалуйста, отправь правильную ссылку (с http:// или https://).")

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
