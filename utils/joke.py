import requests
import json
import aiogram
from config import config
from aiogram.types import FSInputFile, CallbackQuery, Message, InputMediaPhoto
import database.requests as rq

def fetch_joke(retry_count=3):
    url = "http://rzhunemogu.ru/RandJSON.aspx?CType=1"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            clean_content = response.text.replace('\n', '\\n').replace('\r', '\\r')
            try:
                joke_data = json.loads(clean_content)
                return joke_data.get("content", "Шутка не найдена.")
            except json.JSONDecodeError as e:
                if retry_count > 0:
                    print(f"Ошибка декодирования JSON, попытка {3 - retry_count + 1}: {e}")
                    return fetch_joke(retry_count) 
            except aiogram.exceptions.TelegramBadRequest as e:
                print(f"Ошибка слишком большая шутка, попытка {3 - retry_count + 1}: {e}")
                return fetch_joke(retry_count) 
        else:
            return "Не удалось загрузить шутку: HTTP статус " + str(response.status_code)
    except Exception as e:
        return f"Произошла ошибка при запросе: {e}"


async def send_response_joke(event, from_command=None, repeat=None, reply_markup=None):
    joke = fetch_joke()
    photo_path = f"{config['asset_directory']}joke.jpg"
    photo = FSInputFile(photo_path)
    if from_command:
        if isinstance(event, CallbackQuery):
            await event.message.answer_photo(photo=photo, caption=joke, reply_markup=reply_markup)
        elif isinstance(event, Message):
            await event.answer_photo(photo=photo, caption=joke, reply_markup=reply_markup)
    elif repeat:
        if isinstance(event, CallbackQuery):
            await event.message.edit_caption(caption=joke, reply_markup=reply_markup)
        elif isinstance(event, Message):
            await event.edit_caption(caption=joke, reply_markup=reply_markup)
    else:
        photo = InputMediaPhoto(media=photo,caption=joke)
        if isinstance(event, CallbackQuery):
            await event.message.edit_media(media=photo, caption=joke, reply_markup=reply_markup)
        elif isinstance(event, Message):
            await event.edit_media(media=photo, caption=joke, reply_markup=reply_markup)


async def handle_joke_interaction(event, from_command=None, repeat=None, reply_markup=None):
    await rq.update_last_command(event.from_user.id, "joke")
    await send_response_joke(event, from_command=from_command, repeat=repeat, reply_markup=reply_markup)