from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from utils.news import parse_news, categories
from aiogram.filters.callback_data import CallbackData

def main_menu():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Погода", callback_data="weather"))
    builder.add(InlineKeyboardButton(text="Новости", callback_data="select_category"))
    builder.add(InlineKeyboardButton(text="Шутка", callback_data="joke"))
    builder.row(
        InlineKeyboardButton(text="Инфо", callback_data="info"),
        InlineKeyboardButton(text="Настройки", callback_data="settings")
    )
    return builder.as_markup()


async def select_news_category():
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.add(InlineKeyboardButton(text=category, callback_data=f"category_{category}"))
    builder.row(InlineKeyboardButton(text="В главное меню", callback_data="main_menu"))
    return builder.adjust(2).as_markup()


class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int
    category: str 


def paginator(page: int = 0, category: str = "", total_pages: int = 0):
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(text="В главное меню", callback_data="main_menu"),
        InlineKeyboardButton(text="К выбору категории", callback_data="select_category")
    )
    
    builder.row(
        InlineKeyboardButton(text="⬅️", callback_data=Pagination(action="prev", page=page-1, category=category).pack()),
        InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="current_page"),
        InlineKeyboardButton(text="➡️", callback_data=Pagination(action="next", page=page+1, category=category).pack())
    )

    return builder.as_markup()


def set_weather():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Отправить геолокацию 🚩", request_location=True))
    return builder.adjust(1).as_markup(resize_keyboard=True)


def show_weather():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="В главное меню", callback_data="main_menu"),
        InlineKeyboardButton(text="Сменить город", callback_data="change_location")
    )
    return builder.as_markup(resize_keyboard=True)

def joke():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="В главное меню", callback_data="main_menu"),
                InlineKeyboardButton(text="Ещё", callback_data="new_joke"))
    return builder.as_markup(resize_keyboard=True)