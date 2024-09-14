import telebot
from telebot.types import Message
from playwright.sync_api import sync_playwright
import os

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
TOKEN = '7332817569:AAG3l2IJugs0geomZCaT9k-YoVcwBXcHAgs'

bot = telebot.TeleBot(TOKEN)

user_states = {}

@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.reply_to(message, 'Привет! Отправь мне URL сайта, где есть форма для отправки сообщений.')
    user_states[message.from_user.id] = 'waiting_for_url'

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'waiting_for_url')
def get_url(message: Message):
    url = message.text
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    user_states[message.from_user.id] = {'state': 'waiting_for_text', 'url': url}
    bot.reply_to(message, 'Теперь отправь мне текст, который нужно ввести в форму.')

@bot.message_handler(func=lambda message: isinstance(user_states.get(message.from_user.id), dict) and user_states[message.from_user.id]['state'] == 'waiting_for_text')
def fill_form(message: Message):
    url = user_states[message.from_user.id]['url']
    text_to_fill = message.text

    bot.reply_to(message, 'Заполняю форму...')

    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        page.goto(url)
        
        try:
            # Ищем последнее текстовое поле на странице
            textareas = page.query_selector_all('textarea')
            if textareas:
                last_textarea = textareas[-1]
                last_textarea.fill(text_to_fill)
                bot.reply_to(message, 'Форма заполнена успешно.')
                screenshot = page.screenshot()
                bot.send_photo(message.chat.id, screenshot)
            else:
                bot.reply_to(message, 'На странице не найдено текстовых полей.')
        except Exception as e:
            bot.reply_to(message, f'Произошла ошибка: {str(e)}')
        finally:
            browser.close()

    user_states[message.from_user.id] = 'waiting_for_url'

@bot.message_handler(commands=['cancel'])
def cancel(message: Message):
    user_states[message.from_user.id] = 'waiting_for_url'
    bot.reply_to(message, 'Операция отменена. Отправьте новый URL, когда будете готовы.')

if __name__ == '__main__':
    bot.polling(none_stop=True)
