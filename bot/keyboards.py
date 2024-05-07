from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from utils.news import parse_news, categories


main_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Погода"), KeyboardButton(text="Новости"), KeyboardButton(text="Шутка")],
                                          [KeyboardButton(text="Инфо"), KeyboardButton(text="Настройки")]],
                                          resize_keyboard=True,
                                          input_field_placeholder="Выберите пункт меню:")

async def select_news_category():
    keyboard = ReplyKeyboardBuilder()
    for category in categories:
        keyboard.add(KeyboardButton(text=category))
    keyboard.add(KeyboardButton(text="В главное меню"))
    return  keyboard.adjust(3).as_markup(resize_keyboard=True)

async def news(category):
    news_data = parse_news(category)
    for news_item in news_data:
        print("Title:", news_item["title"])
        print("Description:", news_item["description"])
        print("Link:", news_item["link"])
        print("Href:", news_item["href"])
    pass