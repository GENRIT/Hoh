import telebot
from playwright.sync_api import sync_playwright
import os

# Токен вашего телеграм-бота
API_TOKEN = '7332817569:AAG3l2IJugs0geomZCaT9k-YoVcwBXcHAgs'

# Создаем экземпляр бота
bot = telebot.TeleBot(API_TOKEN)

# Функция для заполнения поля и получения сообщений с сайта
def fill_form_and_get_response(url, user_message):
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)  # Запускаем браузер в headless режиме
            page = browser.new_page()
            print(f"Открываю страницу: {url}")
            page.goto(url)
            page.wait_for_load_state("networkidle")  # Ждем, пока загрузка страницы завершится
            
            # Ищем поле для сообщения (например, по имени поля)
            print("Ищу поле с надписью 'Message'")
            message_field_selector = 'textarea[name="message"], input[name="message"], textarea, input'  # Общий селектор
            
            # Проверяем, существует ли элемент
            message_field = page.query_selector(message_field_selector)
            if message_field:
                print(f"Нашел поле, заполняю его текстом: {user_message}")
                page.fill(message_field_selector, user_message)  # Заполняем поле сообщением от пользователя
                page.keyboard.press('Enter')  # Имитация нажатия на Enter после ввода текста
            else:
                raise Exception("Поле 'Message' не найдено на странице.")
            
            # Ждем появления ответа на сайте (например, в блоке с чат-сообщениями)
            print("Ожидание появления сообщения на сайте...")
            page.wait_for_timeout(3000)  # Ждем 3 секунды для обновления страницы
            
            # Ищем элемент с ответом (нужно изменить селектор в зависимости от сайта)
            response_selector = 'div.chat-response'  # Замените на актуальный селектор блока с ответами
            response_element = page.query_selector(response_selector)
            if response_element:
                response_text = response_element.text_content()  # Получаем текст ответа
                print(f"Получено сообщение с сайта: {response_text}")
                return response_text
            else:
                raise Exception("Ответное сообщение не найдено на странице.")
    
    except Exception as e:
        print(f"Ошибка при получении сообщения: {e}")
        return None

# Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку и текст, который ты хочешь вставить, и я покажу ответ с сайта.")

# Обрабатываем все текстовые сообщения
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Предполагаем, что пользователь отправляет URL и сообщение через запятую (например, "http://example.com, Привет!")
    if "," in message.text:
        url, user_message = [x.strip() for x in message.text.split(",", 1)]
        if url.startswith("http://") or url.startswith("https://"):
            bot.reply_to(message, "Подожди, вставляю сообщение и получаю ответ с сайта...")
            response_text = fill_form_and_get_response(url, user_message)
            if response_text:
                bot.reply_to(message, f"ChatGPT: {response_text}")
            else:
                bot.reply_to(message, "Не удалось получить ответ с сайта. Попробуйте еще раз.")
        else:
            bot.reply_to(message, "Пожалуйста, отправь правильную ссылку (с http:// или https://).")
    else:
        bot.reply_to(message, "Пожалуйста, отправь ссылку и сообщение через запятую (например, http://example.com, Привет!).")

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
