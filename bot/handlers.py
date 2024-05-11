from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, URLInputFile, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import config
import bot.keyboards as kb
import database.requests as rq
import utils.weather as weather
import utils.news as news
import utils.joke as joke


router = Router()


class Location(StatesGroup):
    city = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id, message.from_user.username)
    photo_path = f"{config['asset_directory']}main_menu.png"
    photo = FSInputFile(photo_path)
    await rq.update_last_command(message.from_user.id, "start")
    await message.answer_photo(photo=photo, caption="Добро пожаловать в тестового бота!", reply_markup=kb.main_menu())


@router.callback_query(kb.Pagination.filter(F.action.in_(["prev", "next"])))
async def pagination_handler(call: CallbackQuery, callback_data: kb.Pagination):
    current_page_number = int(callback_data.page)
    category = callback_data.category
    news_items = news.parse_news(category)
    max_pages = len(news_items) - 1
    
    if current_page_number < 0 or current_page_number > max_pages:
        await call.answer("Вы достигли предела страниц.")
        return
    
    await call.message.edit_media(news.format_news_item(news_items[current_page_number]),
                                  reply_markup=kb.paginator(current_page_number, category, max_pages+1))


@router.callback_query()
async def handle_callback_query(callback_query: CallbackQuery, state: FSMContext):
    action = callback_query.data
    await rq.update_last_command(callback_query.from_user.id, callback_query.data)
    if action.startswith("category_"):
        category = action.split("_")[1]
        news_items = news.parse_news(category)

        if news_items:
            await callback_query.message.edit_media(news.format_news_item(news_items[0]),
                                          reply_markup=kb.paginator(0, category, len(news_items)))
        else:
            await callback_query.message.edit_text("Новостей в данной категории нет.")
    match action:
        case "main_menu":
            photo_path = f"{config['asset_directory']}main_menu.png"
            photo = InputMediaPhoto(media=FSInputFile(photo_path), caption= "Главное меню")
            await callback_query.message.edit_media(media=photo, caption="Главное меню", reply_markup=kb.main_menu())
            await rq.update_last_command(callback_query.from_user.id, callback_query.data)

        case "select_category":
            await news.handle_select_category_interaction(callback_query, reply_markup=kb.select_news_category())
        case "weather":
            await handle_weather_interaction(callback_query, state)
        case "change_location":
            await rq.delete_location(callback_query.from_user.id)
            await handle_weather_interaction(callback_query, state)
            await callback_query.answer()
        case "current_page":
            await callback_query.answer()
        case "joke":
            await joke.handle_joke_interaction(callback_query, reply_markup=kb.joke())
        case "new_joke":
            await joke.handle_joke_interaction(callback_query, repeat=True, reply_markup=kb.joke())
        case "info":
            await handle_info_interaction(callback_query)
        case "settings":
            await handle_settings_interaction(callback_query)
        case _:
            await pagination_handler(callback_query)
            await callback_query.answer()


@router.message(F.text.startswith("/"))
async def handle_commands(message: Message, state: FSMContext):
    match message.text:
        case "/weather":
            await handle_weather_interaction(message, state, from_command=True)
        case "/news":
            await news.handle_select_category_interaction(message, reply_markup=kb.select_news_category(), from_command=True)
        case "/info":
            await handle_info_interaction(message, from_command=True)
        case "/settings":
            await handle_settings_interaction(message, from_command=True)
        case "/joke":
            await joke.handle_joke_interaction(message, from_command=True, reply_markup=kb.joke())
        case _:
            await message.answer("Данной комманды не существует.")


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


async def send_response_info(event, from_command=None):
    help_text = (
        "<b>Доступные команды:</b>\n"
        "/start - перезапустить бота\n"
        "/news - получить последние новости\n"
        "/weather - получить погоду\n"
        "/joke - получить случайную шутку\n"
        "/info - справочная информация\n"
        "/settings - настройки бота\n"
    )
    photo_path = f"{config['asset_directory']}help.png"
    photo = FSInputFile(photo_path)
    if from_command:
        if isinstance(event, CallbackQuery):
            await event.message.answer_photo(photo=photo, caption=help_text, parse_mode="HTML", reply_markup=kb.help())
        elif isinstance(event, Message):
            await event.answer_photo(photo=photo, caption=help_text, parse_mode="HTML", reply_markup=kb.help())
    else:
        photo = InputMediaPhoto(media=photo, caption=help_text, parse_mode="HTML")
        if isinstance(event, CallbackQuery):
            await event.message.edit_media(media=photo, caption=help_text, reply_markup=kb.help())
        elif isinstance(event, Message):
            await event.edit_media(media=photo, caption=help_text, reply_markup=kb.help())


async def send_response_settings(event, from_command=None):
    settings_text = (
        "Вы можете настроить следующие параметры:\n"
        "- <b>Регион</b>: сменить регион погоды.\n"
    )
    photo_path = f"{config['asset_directory']}settings.png"
    photo = FSInputFile(photo_path)
    if from_command:
        if isinstance(event, CallbackQuery):
            await event.message.answer_photo(photo=photo, caption=settings_text, parse_mode="HTML", reply_markup=kb.settings())
        elif isinstance(event, Message):
            await event.answer_photo(photo=photo, caption=settings_text, parse_mode="HTML", reply_markup=kb.settings())
    else:
        photo = InputMediaPhoto(media=photo, caption=settings_text, parse_mode="HTML")
        if isinstance(event, CallbackQuery):
            await event.message.edit_media(media=photo, caption=settings_text, reply_markup=kb.settings())
        elif isinstance(event, Message):
            await event.edit_media(media=photo, caption=settings_text, reply_markup=kb.settings())


async def handle_info_interaction(event, from_command=None):
    await rq.update_last_command(event.from_user.id, "help")
    await send_response_info(event, from_command=from_command)


async def handle_settings_interaction(event, from_command=None):
    await rq.update_last_command(event.from_user.id, "settings")
    await send_response_settings(event, from_command=from_command)


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