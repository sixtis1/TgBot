from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import F, Router

import bot.keyboards as kb


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать в тестового бота!", reply_markup=kb.main_menu)


@router.message(Command('help'))
async def cmd_help(message: Message):
    pass


@router.message(Command('settings'))
async def cmd_help(message: Message):
    pass


@router.message(Command('weather'))
async def cmd_help(message: Message):
    pass


@router.message(Command('news'))
async def select_news_cat(message: Message):
    await message.answer("Выберите категорию новостей", reply_markup=await kb.select_news_category())

@router.message(F.text == "Новости")
async def select_news_cat(message: Message):
    await message.answer("Выберите категорию новостей", reply_markup=await kb.select_news_category())

@router.message(F.text == "В главное меню")
async def main_menu(message: Message):
    await message.answer("Главное меню", reply_markup=kb.main_menu)

@router.message(Command('joke'))
async def cmd_help(message: Message):
    pass