from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, URLInputFile, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram import F, Router
from utils.news import parse_news
from utils.joke import fetch_joke
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import bot.keyboards as kb
import database.requests as rq
import utils.weather as weather

router = Router()
asset_string = "assets/"


class Location(StatesGroup):
    city = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id, message.from_user.username)
    photo_path = f"{asset_string}main_menu.png"
    photo = FSInputFile(photo_path)
    await rq.update_last_command(message.from_user.id, "start")
    await message.answer_photo(photo=photo, caption="Добро пожаловать в тестового бота!", reply_markup=kb.main_menu())


@router.callback_query(kb.Pagination.filter(F.action.in_(["prev", "next"])))
async def pagination_handler(call: CallbackQuery, callback_data: kb.Pagination):
    page_num = int(callback_data.page)
    category = callback_data.category
    news_items = parse_news(category)
    max_pages = len(news_items) - 1
    
    if page_num < 0 or page_num > max_pages:
        await call.answer("Вы достигли предела страниц.")
        return
    
    caption = f'<b>{news_items[page_num]["title"]}</b>\n'
    caption += f'{news_items[page_num]["description"]}\n'
    caption += f'<a href="{news_items[page_num]["link"]}"><b>Ссылка</b></a>'
    photo = InputMediaPhoto(media=URLInputFile(news_items[page_num]["href"]), 
                            caption=caption, 
                            parse_mode="HTML")
    await call.message.edit_media(media=photo, 
                                  caption=caption,
                                  reply_markup=kb.paginator(page_num, category, max_pages+1))


@router.callback_query()
async def handle_callback_query(call: CallbackQuery, state: FSMContext):
    action = call.data
    await rq.update_last_command(call.from_user.id, call.data)
    if action.startswith("category_"):
        category = action.split("_")[1]
        news_items = parse_news(category)

        if news_items:
            caption = f'<b>{news_items[0]["title"]}</b>\n'
            caption += f'{news_items[0]["description"]}\n'
            caption += f'<a href="{news_items[0]["link"]}"><b>Ссылка</b></a>'
            photo = InputMediaPhoto(media=URLInputFile(news_items[0]["href"]), 
                                    caption=caption,
                                    parse_mode="HTML")
            await call.message.edit_media(media=photo, 
                                          caption=caption,
                                          reply_markup=kb.paginator(0, category, len(news_items)))
        else:
            await call.message.edit_text("Новостей в данной категории нет.")

    elif action == "main_menu":
        photo_path = f"{asset_string}main_menu.png"
        photo = InputMediaPhoto(media=FSInputFile(photo_path), caption= "Главное меню")
        await call.message.edit_media(media=photo, caption="Главное меню", reply_markup=kb.main_menu())
        await rq.update_last_command(call.from_user.id, call.data)

    elif action == "select_category":
        photo_path = f"{asset_string}{action}.jpg"
        photo_media = InputMediaPhoto(media=FSInputFile(photo_path))
        await call.message.edit_media(media=photo_media)
        await call.message.edit_caption("Выберите категорию новостей", reply_markup=await kb.select_news_category())
        await rq.update_last_command(call.from_user.id, call.data)

    elif action == "weather":
        await handle_weather_interaction(call, state)
        await call.answer()
    elif action == "change_location":
        await rq.delete_location(call.from_user.id)
        await handle_weather_interaction(call, state)
        await call.answer()
    elif action == "current_page":
        await call.answer()
    
    elif action == "joke":
        await handle_joke_interaction(call)
    elif action == "new_joke":
        await handle_joke_interaction(call, repeat=True)

    else:
        await pagination_handler(call)


@router.callback_query(F.data == "noop")
async def noop_handler(call: CallbackQuery):
    await call.answer(cache_time=60) 


async def send_response_weather(event, data, first_time=None, from_command=None, reply_markup=None):
    if first_time:
        if isinstance(event, CallbackQuery):
            await event.message.answer(data, reply_markup=reply_markup)
        elif isinstance(event, Message):
            await event.answer(data, reply_markup=reply_markup)
    elif from_command:
        caption = data[0]
        photo = URLInputFile(data[1])
        if isinstance(event, CallbackQuery):
            await event.message.answer_photo(photo=photo, caption=caption, reply_markup=reply_markup)
        elif isinstance(event, Message):
            await event.answer_photo(photo=photo, caption=caption, reply_markup=reply_markup)
    else:
        caption = data[0]
        photo = URLInputFile(data[1])
        media = InputMediaPhoto(media=photo, caption=caption)
        if isinstance(event, CallbackQuery):
            await event.message.edit_media(media=media, caption=caption, reply_markup=reply_markup)
        elif isinstance(event, Message):
            await event.edit_media(media=media, caption=caption, reply_markup=reply_markup)


async def handle_weather_interaction(event, state: FSMContext, from_command=None):
    await rq.update_last_command(event.from_user.id, "weather")
    data = await rq.check_location(event.from_user.id)
    if data == 0:
        await state.set_state(Location.city)
        await send_response_weather(event, "Введите название города или отправьте свою геолокацию:", first_time=True, reply_markup=kb.set_weather())
    elif data[0] == "city":
        weather_info = await weather.get_weather_by_city(data[1])
        await send_response_weather(event, weather_info, reply_markup=kb.show_weather(), from_command=from_command)
    elif data[0] == "coords":
        weather_info = await weather.get_weather_by_coords(data[1])
        await send_response_weather(event, weather_info, reply_markup=kb.show_weather(), from_command=from_command)    


async def send_response_joke(event, from_command=None, repeat=None, reply_markup=None):
    joke = fetch_joke()
    photo_path = f"{asset_string}joke.jpg"
    photo = FSInputFile(photo_path)
    if from_command:
        if isinstance(event, CallbackQuery):
            await event.message.answer_photo(photo=photo, caption=joke, reply_markup=kb.joke())
        elif isinstance(event, Message):
            await event.answer_photo(photo=photo, caption=joke, reply_markup=kb.joke())
    elif repeat:
        if isinstance(event, CallbackQuery):
            await event.message.edit_caption(caption=joke, reply_markup=kb.joke())
        elif isinstance(event, Message):
            await event.edit_caption(caption=joke, reply_markup=kb.joke())
    else:
        photo = InputMediaPhoto(media=photo,caption=joke)
        if isinstance(event, CallbackQuery):
            await event.message.edit_media(media=photo, caption=joke, reply_markup=kb.joke())
        elif isinstance(event, Message):
            await event.edit_media(media=photo, caption=joke, reply_markup=kb.joke())


async def handle_joke_interaction(event, from_command=None, repeat=None):
    await rq.update_last_command(event.from_user.id, "joke")
    await send_response_joke(event, from_command=from_command, repeat=repeat)


@router.message(Location.city)
async def set_location(message: Message, state: FSMContext):
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        coords = f"{lat},{lon}"
        weather_data = await weather.get_weather_by_coords(coords)
        reply = weather_data[0]
        photo = URLInputFile(weather_data[1])
        await rq.update_coord(message.from_user.id, lat, lon)
        await message.answer("Координаты успешно сохранены", reply_markup=ReplyKeyboardRemove())
        await message.answer_photo(photo=photo, caption=reply, reply_markup=kb.show_weather())
        await state.clear()
    elif message.text:
        weather_response = await weather.get_weather_by_city(message.text)
        if weather_response[0] != "Город не найден, пожалуйста, проверьте название и попробуйте снова.":
            await rq.update_city(message.from_user.id, message.text)
            await state.update_data(city=message.text)
            weather_data = await weather.get_weather_by_city(message.text)
            reply = weather_data[0]
            photo = URLInputFile(weather_data[1])
            await message.answer("Город успешно сохранен", reply_markup=ReplyKeyboardRemove())
            await message.answer_photo(photo=photo, caption=reply, reply_markup=kb.show_weather())
            await state.clear()
        else:
            await message.answer("Город не найден, пожалуйста, проверьте название и попробуйте снова.")
            

@router.message(Command('weather'))
async def weather_command(message: Message, state: FSMContext):
    await handle_weather_interaction(message, state, from_command=True)


@router.message(Command('news'))
async def select_news_cat(message: Message):
    await message.answer("Выберите категорию новостей", reply_markup=await kb.select_news_category())


@router.message(Command('help'))
async def cmd_help(message: Message):
    pass


@router.message(Command('settings'))
async def cmd_help(message: Message):
    pass


@router.message(Command('joke'))
async def cmd_joke(message: Message):
    await send_response_joke(message, from_command=True)