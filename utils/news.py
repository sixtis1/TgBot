import feedparser
import database.requests as rq
from aiogram.types import InputMediaPhoto, URLInputFile, FSInputFile, CallbackQuery, Message
from config import config


categories = {
    "В мире": "world/",
    'Политика': "politics/",
    "Проишествия": "incidents/",
    "Наука и техника": "tech/",
    "Военные новости": "army/",
    "Игры": "games/"
    }


def parse_news(rss: str):
    url = "https://news.rambler.ru/rss/"
    news_list = []
    feed = feedparser.parse(url + categories[rss])
    for entry in feed.entries:
        href = [enclosure.get('href', '') for enclosure in entry.enclosures]
        if href:
            href = href[0]
        news_item = {
                    "title": entry.title,
                    "description": entry.description,
                    "link": entry.link,
                    "href": href
                }
        news_list.append(news_item)
    return news_list


def format_news_item(news_item):
    caption = f'<b>{news_item["title"]}</b>\n{news_item["description"]}\n' \
              f'<a href="{news_item["link"]}"><b>Ссылка на новость</b></a>'
    photo = InputMediaPhoto(media=URLInputFile(news_item["href"]), caption=caption, parse_mode="HTML")
    return photo


async def send_response_select_category(event, reply_markup, from_command=None):
    photo_path = f"{config['asset_directory']}select_category.jpg"
    photo = FSInputFile(photo_path)
    caption = "Выберите категорию новостей"
    if from_command:
        if isinstance(event, CallbackQuery):
            await event.message.answer_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=reply_markup)
        elif isinstance(event, Message):
            await event.answer_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=reply_markup)
    else:
        photo = InputMediaPhoto(media=photo, caption=caption, parse_mode="HTML")
        if isinstance(event, CallbackQuery):
            await event.message.edit_media(media=photo, caption=caption, reply_markup=reply_markup)
        elif isinstance(event, Message):
            await event.edit_media(media=photo, caption=caption, reply_markup=reply_markup)   


async def handle_select_category_interaction(event, reply_markup, from_command=None):
    await rq.update_last_command(event.from_user.id, "news")
    await send_response_select_category(event, reply_markup, from_command=from_command)
