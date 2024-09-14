import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from playwright.sync_api import sync_playwright

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
TOKEN = '7332817569:AAG3l2IJugs0geomZCaT9k-YoVcwBXcHAgs'

# Состояния для ConversationHandler
WAITING_FOR_URL, WAITING_FOR_TEXT = range(2)

def start(update, context):
    update.message.reply_text('Привет! Отправь мне URL сайта, где есть форма "Message ChatGPT".')
    return WAITING_FOR_URL

def get_url(update, context):
    url = update.message.text
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    context.user_data['url'] = url
    update.message.reply_text('Теперь отправь мне текст, который нужно ввести в форму.')
    return WAITING_FOR_TEXT

def fill_form(update, context):
    url = context.user_data['url']
    text_to_fill = update.message.text

    update.message.reply_text('Заполняю форму...')

    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        page.goto(url)
        
        try:
            # Ищем текстовое поле рядом с "Message ChatGPT"
            textarea = page.query_selector('textarea[placeholder="Message ChatGPT"]')
            if textarea:
                textarea.fill(text_to_fill)
                update.message.reply_text('Форма заполнена успешно.')
                screenshot = page.screenshot()
                update.message.reply_photo(screenshot)
            else:
                update.message.reply_text('Форма "Message ChatGPT" не найдена на странице.')
        except Exception as e:
            update.message.reply_text(f'Произошла ошибка: {str(e)}')
        finally:
            browser.close()

    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text('Операция отменена.')
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_URL: [MessageHandler(Filters.text & ~Filters.command, get_url)],
            WAITING_FOR_TEXT: [MessageHandler(Filters.text & ~Filters.command, fill_form)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()