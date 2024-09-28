from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from aiogram import F, Router, Bot

from app.database import add_raper_info, add_track_info, select_nick, select_track
from app.keyboards import after_adding_raper_keyboard, add_raper_keyboard, add_track_keyboard


states = Router()


class AddRaper(StatesGroup):
    name = State()
    bio = State()
    link = State()


@states.message(Command("add_raper"))
@states.callback_query(F.data == "add_raper")
async def add_raper(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(AddRaper.name)
    await bot.send_message(callback.from_user.id, "Ники рэперро ворид кунед:")


@states.message(AddRaper.name)
async def add_raper_name(message: Message, state: FSMContext):
    raper_name = message.text.capitalize()
    await state.update_data(name=raper_name)
    result = await select_nick(raper_name)

    if result:
        await message.answer("Рэпер алакай ворид карда шудааст!", reply_markup=after_adding_raper_keyboard(result))
        await state.clear()
    else:
        await state.set_state(AddRaper.bio)
        await message.answer("Биографияи рэперро ворид кунед:")


@states.message(AddRaper.bio)
async def add_raper_bio(message: Message, state: FSMContext):
    await state.update_data(bio=message.text)
    await state.set_state(AddRaper.link)
    await message.answer("Пайвандҳои YouTube, Instagram ва дигар шабакаҳои рэперро ворид кунед:")


@states.message(AddRaper.link)
async def add_raper_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()
    await add_raper_info(data["name"], data["bio"], data["link"])
    await state.clear()
    await message.answer(f"<i>Рэпер <b>{data["nick"]}</b> ворид карда шуд!</i>", reply_markup=after_adding_raper_keyboard(data["name"]))


########## ФУНКЦИЯ ДЛЯ ДОБАВЛЕНИЯ ТРЕКА ##########
class AddTrack(StatesGroup):
    nick = State()
    track_name = State()
    track_link = State()


@states.callback_query(F.data.startswith("add_track_"))
async def add_track(callback: CallbackQuery, state: FSMContext, bot: Bot):
    raper_nick = callback.data.split("_")[-1]
    await state.set_state(AddTrack.nick)
    await state.update_data(nick=raper_nick)
    await state.set_state(AddTrack.track_name)
    await bot.send_message(callback.from_user.id, "Номи трекро ворид кунед:")


@states.message(AddTrack.track_name)
async def add_track_name(message: Message, state: FSMContext):
    track = message.text.strip().capitalize()
    await state.update_data(track_name=track)
    result = await select_track(track)

    if result:
        await state.clear()
        await message.answer("""Ин треки рэпер алакай дохил карда шудааст.
        Шумо метавоне дигар трекро ворид кунед""", reply_markup=add_track_keyboard(result))
    else:
        await message.answer("Пайванд (ссылка)-и трекро ворид кунед:")
        await state.set_state(AddTrack.track_link)


@states.message(AddTrack.track_link)
async def add_track_link(message: Message, state: FSMContext):
    await state.update_data(track_link=message.text)
    data = await state.get_data()
    await state.clear()
    await add_track_info(data["nick"], data["track_name"], data["track_link"])
    await message.answer(f"""Ба рэпер <b>{data["nick"]}</b> трек нав ворид карда шуд!
    \nАгар хоҳед боз трек ворид кардан, пас тугмаи поёнро зер кунед""",
                         reply_markup=add_track_keyboard(data["nick"]))

