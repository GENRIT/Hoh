import telebot
from playwright.sync_api import sync_playwright
import os

# Токен вашего телеграм-бота
API_TOKEN = '7332817569:AAG3l2IJugs0geomZCaT9k-YoVcwBXcHAgs'

# Создаем экземпляр бота
bot = telebot.TeleBot(API_TOKEN)

# Функция для заполнения поля и создания скриншота
def fill_form_and_take_screenshot(url, user_message):
    screenshot_path = "screenshot.png"
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)  # Запускаем браузер в headless режиме
            page = browser.new_page()
            print(f"Открываю страницу: {url}")
            page.goto(url)
            page.wait_for_load_state("networkidle")  # Ждем, пока загрузка страницы завершится
            
            # Ищем поле для сообщения (например, по имени поля)
            print("Ищу поле с надписью 'Message'")
            message_field_selector = 'textarea[name="input"], input[type="text"]'  # Селектор для ввода сообщения

            # Проверяем, существует ли элемент
            message_field = page.query_selector(message_field_selector)
            if message_field:
                print(f"Нашел поле, заполняю его текстом: {user_message}")
                page.fill(message_field_selector, user_message)  # Заполняем поле сообщением от пользователя

                # Находим кнопку отправки
                submit_button_selector = 'button[type="submit"], button[aria-label="Send message"]'
                submit_button = page.query_selector(submit_button_selector)

                if submit_button:
                    print("Найдено! Отправляю сообщение через кнопку.")
                    page.click(submit_button_selector)  # Кликаем по кнопке отправки
                else:
                    print("Кнопка отправки не найдена. Попробую нажать Enter.")
                    page.keyboard.press("Enter")  # Альтернативный способ — нажатие Enter
            else:
                raise Exception("Поле для сообщения не найдено на странице.")

            # Ожидание для рендеринга результатов (лучше дождаться конкретного элемента)
            print("Ожидание 5 секунд перед созданием скриншота...")
            page.wait_for_timeout(5000)  # Задержка в 5 секунд

            # Делаем скриншот
            print(f"Создаю скриншот и сохраняю как: {screenshot_path}")
            page.screenshot(path=screenshot_path, full_page=True)
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
    bot.reply_to(message, "Привет! Отправь мне ссылку и текст, который ты хочешь вставить, и я сделаю скриншот сайта.")

# Обрабатываем все текстовые сообщения
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Предполагаем, что пользователь отправляет URL и сообщение через запятую (например, "http://example.com, Привет!")
    if "," in message.text:
        url, user_message = [x.strip() for x in message.text.split(",", 1)]
        if url.startswith("http://") or url.startswith("https://"):
            bot.reply_to(message, "Подожди, вставляю сообщение и делаю скриншот сайта...")
            screenshot = fill_form_and_take_screenshot(url, user_message)
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
    else:
        bot.reply_to(message, "Пожалуйста, отправь ссылку и сообщение через запятую (например, http://example.com, Привет!).")

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
