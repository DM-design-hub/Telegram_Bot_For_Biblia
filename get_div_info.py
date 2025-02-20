from bs4 import BeautifulSoup, NavigableString
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO

# Ваш токен API для Telegram бота
TELEGRAM_TOKEN = '8010314114:AAGFXUWSJPV-eNRQY72Ks-LpksNDlNqv3fQ'

# URL страницы, которую вы хотите проанализировать
url = 'https://belinkaluga.ru/'
url_sait = 'https://belinkaluga.ru/'
url_vk = 'https://vk.com/belinklg'
url_ok = 'https://ok.ru/group/56448303235218'
url_virtual_info = 'https://belinkaluga.ru/virtualnaya-spravka/'
url_bibl_info = 'https://belinkaluga.ru/udaljonnaya-zapis-v-biblioteku/?doing_wp_cron=1739953917.3443040847778320312500'
exclude_text = 'Афиша мероприятий'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Создаем клавиатуру с кнопкой
    keyboard = [
        [KeyboardButton("Анонс")],
        [KeyboardButton("Афиша")],
        [KeyboardButton("О нас")],
        [KeyboardButton("Сервисы")]
        
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text('Привет! Я бот, который парсит веб-страницы. Нажмите кнопку "Анонс", чтобы получить данные, или "О нас", чтобы перейти на сайт.', reply_markup=reply_markup)

async def anons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Отправляем HTTP-запрос к URL
    response = requests.get(url)

    # Проверяем, что запрос прошел успешно
    if response.status_code == 200:
        # Создаем объект BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Находим все элементы <div> с заданным классом
        divs = soup.find_all('div', class_='news-post')

        for div in divs:
            # Проверяем, содержит ли <div> исключаемый текст
            if exclude_text in div.get_text():
                # Удаляем <div> и его содержимое
                div.decompose()
                continue

        # Проходим по всем найденным элементам <div>
        for div in divs:
            # Удаляем все внутренние <div> с определенным классом
            for inner_div in div.find_all('div', class_='block-meta'):
                inner_div.replace_with(NavigableString(' '))

            # Извлекаем текст из найденного <div>
            text_content = div.get_text(strip=True, separator=' ')

            # Проверяем, что текст не пустой
            if text_content:
                # Отправляем текст в Telegram
                await update.message.reply_text(text_content)

            # Находим все теги <img> внутри найденного <div>
            img_tags = div.find_all('img')

            # Проходим по всем найденным тегам <img> и загружаем изображения
            for img in img_tags:
                img_url = img.get('src')
                if img_url:
                    # Проверяем, является ли URL относительным
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = requests.compat.urljoin(url, img_url)

                    # Загружаем изображение
                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        # Отправляем изображение в Telegram
                        await update.message.reply_photo(photo=BytesIO(img_response.content))
                    else:
                        await update.message.reply_text(f"Не удалось загрузить изображение: {img_url}")
    else:
        await update.message.reply_text(f"Ошибка при запросе страницы: {response.status_code}")


async def afisha(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Отправляем HTTP-запрос к URL
    response = requests.get(url)

    # Проверяем, что запрос прошел успешно
    if response.status_code == 200:
        # Создаем объект BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Находим все элементы <div> с заданным классом
        divs = soup.find_all('div', class_='news-post')

        for div in divs:
            # Проверяем, содержит ли <div> исключаемый текст
            if exclude_text not in div.get_text():
                # Удаляем <div> и его содержимое
                div.decompose()
                continue

        # Находим все теги <a> внутри найденного <div>
        a_tags = div.find_all('a')
        count_a_href=0
        # Проходим по всем найденным тегам <a> и извлекаем ссылки
        for a in a_tags:
            if count_a_href != 0:
                break
            link_url = a.get('href')
            count_a_href +=1
            if link_url:
                # Проверяем, является ли URL относительным
                if not link_url.startswith(('http://', 'https://')):
                    link_url = requests.compat.urljoin(url, link_url)

                # Отправляем ссылку в Telegram
                #await update.message.reply_text(f"Ссылка: {link_url}")

                # Отправляем HTTP-запрос к найденной ссылке
                response = requests.get(link_url)

                # Проверяем, что запрос прошел успешно
                if response.status_code == 200:
                    # Создаем объект BeautifulSoup для парсинга HTML
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Находим все элементы <div> с заданным классом
                    divs = soup.find_all('div', class_='content-area')

                    # Проходим по всем найденным элементам <div>
                    for div in divs:
                        # Находим все теги <img> внутри найденного <div>
                        img_tags = div.find_all('img')

                        # Проходим по всем найденным тегам <img> и загружаем изображения
                        for img in img_tags:
                            img_url = img.get('src')
                            if img_url:
                                # Проверяем, является ли URL относительным
                                if not img_url.startswith(('http://', 'https://')):
                                    img_url = requests.compat.urljoin(url, img_url)

                                # Загружаем изображение
                                img_response = requests.get(img_url)
                                if img_response.status_code == 200:
                                    # Отправляем изображение в Telegram
                                    await update.message.reply_photo(photo=BytesIO(img_response.content))
                                else:
                                    await update.message.reply_text(f"Не удалось загрузить изображение: {img_url}")
                else:
                    await update.message.reply_text(f"Ошибка при запросе страницы: {response.status_code}")
            break
    else:
        await update.message.reply_text(f"Ошибка при запросе страницы: {response.status_code}")        

async def open_site(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Создаем inline-клавиатуру с кнопкой для открытия сайта
    keyboard = [
        [InlineKeyboardButton("Наш сайт", url=url_sait)],
        [InlineKeyboardButton("ВК", url=url_vk)],
        [InlineKeyboardButton("Одноклассники", url=url_ok)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Нажмите кнопку ниже, чтобы открыть:', reply_markup=reply_markup)

async def virtual_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Создаем inline-клавиатуру с кнопкой для открытия сайта
    keyboard = [
        [InlineKeyboardButton("Виртуальная справка", url=url_virtual_info)],
        [InlineKeyboardButton("Онлайн запись в библиотеку", url=url_bibl_info)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Нажмите кнопку ниже, чтобы открыть сервисы:', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Проверяем, нажата ли кнопка "Парсить страницу" или "Открыть сайт"
    if update.message.text == "Анонс":
        await anons(update, context)
    elif update.message.text == "Афиша":
        await afisha(update,context)
    elif update.message.text == "О нас":
        await open_site(update, context)
    elif update.message.text == "Сервисы":
        await virtual_info(update, context)


def main() -> None:
    # Создаем экземпляр ApplicationBuilder и передаем ему токен API
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Регистрируем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
