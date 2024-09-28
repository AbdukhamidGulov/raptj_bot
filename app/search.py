from random import choice
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import F, Router, Bot

from app.database import select_nick, get_all_rapers, get_raper_info
from app.keyboards import add_raper_keyboard, raper_found_keyboard, raper_tracks_keyboard


searching = Router()
LIST_IS_EMPTY = "Руйхати рэперҳо холи ҳаст, аввалин рэперро ворид кунед"

class SearchStates(StatesGroup):
    raper_nick = State()


@searching.message(Command("search"))
@searching.callback_query(F.data == "search")
async def search(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(callback.from_user.id, "Ники рэперро ворид кунед:")
    await state.set_state(SearchStates.raper_nick)


@searching.message(SearchStates.raper_nick)
async def process_search(message: Message, state: FSMContext):
    raper_nick = message.text.strip().capitalize()
    result = await select_nick(raper_nick)

    if not result:
        await message.answer("Рэпер ёфт нашуд!\nБарои рэперро дохил кардан тугмаи поёнро пахш кунед!",
                             reply_markup=add_raper_keyboard)
    else:
        await state.update_data(raper_nick=raper_nick)
        await message.answer(f"Рэпер: <b>{result.Raper.nick}</b> ёфт шуд", reply_markup=raper_found_keyboard(raper_nick))


@searching.message(Command("random"))
@searching.callback_query(F.data == "random")
async def random(callback: CallbackQuery, state: FSMContext, bot: Bot):
    rappers = await get_all_rapers()
    if not rappers:
        await bot.send_message(callback.from_user.id, LIST_IS_EMPTY, reply_markup=add_raper_keyboard)
    else:
        raper_nick = choice(rappers)
        await bot.send_message(callback.from_user.id, f"<b>{raper_nick}</b> тасодуфан интихоб шуд!")
        await state.update_data(raper_nick=raper_nick)
        await info_about_raper(callback, state, bot)


@searching.message(Command("latest"))
@searching.callback_query(F.data == "latest")
async def latest(callback: CallbackQuery, state: FSMContext, bot: Bot):
    rapers = await get_all_rapers()

    if not rapers:
        await bot.send_message(callback.from_user.id, LIST_IS_EMPTY, reply_markup=add_raper_keyboard)
    else:
        raper_nick = rapers[-1]
        await bot.send_message(callback.from_user.id, f"Охирон рэпери воридшуда: <b>{raper_nick}</b>")
        await state.update_data(raper_nick=raper_nick)
        await info_about_raper(callback, state, bot)


@searching.message(Command("info_about_raper"))
@searching.callback_query(F.data == "info_about_raper")
async def info_about_raper(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    raper_nick = data.get("raper_nick")
    if not raper_nick:
        await search(callback, state, bot)
    raper_info = await get_raper_info(raper_nick)
    if not raper_info:
        await bot.send_message(callback.from_user.id, "Маълумот оиди рэпер ёфт нашуд.")
    else:
        bio = raper_info.bio
        links = raper_info.links
        await bot.send_message(callback.from_user.id, f"""Биография: {bio}\n\nСсылки:\n{links}
Агар хоҳед трекҳои рэпер <b>{raper_nick}</b> бинет пас тугмаи зерро пахш кунед""",
                               reply_markup=raper_tracks_keyboard(raper_nick))
