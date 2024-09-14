import telebot
from playwright.sync_api import sync_playwright
import os
import time

# Токен вашего телеграм-бота
API_TOKEN = '7332817569:AAG3l2IJugs0geomZCaT9k-YoVcwBXcHAgs'

# Создаем экземпляр бота
bot = telebot.TeleBot(API_TOKEN)

# Функция для заполнения поля и создания скриншота
def fill_form_and_take_screenshot(url, user_message):
    screenshot_path = "screenshot.png"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            print(f"Открываю страницу: {url}")
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            print("Ожидание загрузки страницы...")
            page.wait_for_load_state("domcontentloaded")
            
            print("Поиск поля ввода...")
            input_selector = 'textarea, input[type="text"]'
            page.wait_for_selector(input_selector, state="visible", timeout=10000)
            
            print(f"Ввод сообщения: {user_message}")
            page.fill(input_selector, user_message)
            
            print("Поиск кнопки отправки...")
            send_button_selector = 'button[type="submit"], button:has-text("Send")'
            send_button = page.query_selector(send_button_selector)
            
            if send_button:
                print("Нажатие кнопки отправки...")
                send_button.click()
            else:
                print("Кнопка не найдена, нажимаю Enter...")
                page.keyboard.press("Enter")
            
            print("Ожидание ответа...")
            time.sleep(10)  # Даем время на получение ответа
            
            print("Создание скриншота...")
            page.screenshot(path=screenshot_path, full_page=True)
            
            context.close()
            browser.close()
            print("Браузер закрыт.")

        if not os.path.exists(screenshot_path):
            raise Exception("Скриншот не был сохранен.")
        
        return screenshot_path
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        return None

# Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку и текст, который ты хочешь вставить, и я сделаю скриншот сайта.")

# Обрабатываем все текстовые сообщения
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if "," in message.text:
        url, user_message = [x.strip() for x in message.text.split(",", 1)]
        if url.startswith("http://") or url.startswith("https://"):
            bot.reply_to(message, "Подожди, вставляю сообщение и делаю скриншот сайта...")
            screenshot = fill_form_and_take_screenshot(url, user_message)
            if screenshot:
                try:
                    with open(screenshot, 'rb') as screenshot_file:
                        bot.send_photo(message.chat.id, screenshot_file)
                    os.remove(screenshot)  # Удаляем файл после отправки
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