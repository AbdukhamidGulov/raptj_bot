from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router, Bot

from app.database import get_all_rapers, get_tracks_by_raper_name
from app.keyboards import add_raper_keyboard, add_track_keyboard, get_pagination_keyboard
from app.search import LIST_IS_EMPTY

get_values = Router()
ITEMS_PER_PAGE = 5


class RaperStates(StatesGroup):
    raper_list = State()


async def get_raper_list(state: FSMContext):
    data = await state.get_data()
    raper_cache = data.get("raper_cache")
    if raper_cache is None:
        raper_cache = await get_all_rapers()
        await state.update_data(raper_cache=raper_cache)

    return raper_cache if raper_cache else []


async def get_cached_raper_list(state: FSMContext):
    data = await state.get_data()
    rapers = data.get("raper_list")

    if rapers is None:
        rapers = await get_raper_list(state)
        await state.update_data(raper_list=rapers)

    return rapers


async def raper_list(user_id: int, page: int, state: FSMContext, bot: Bot):
    rapers = await get_cached_raper_list(state)

    if not rapers:
        await bot.send_message(user_id, LIST_IS_EMPTY, reply_markup=add_raper_keyboard)
        return

    current_rapers, total_pages = paginate(rapers, page, ITEMS_PER_PAGE)
    rapers_str = "\n".join(current_rapers)
    await bot.send_message(user_id, f"""<b>"Руйхати рэперҳо:"</b>
{rapers_str}""", reply_markup=get_pagination_keyboard(page, total_pages, "raper"))


@get_values.message(Command("list"))
async def raper_list_message(message: Message, state: FSMContext, bot: Bot):
    await raper_list(user_id=message.from_user.id, page=0, state=state, bot=bot)


@get_values.callback_query(F.data == "raper_list")
@get_values.callback_query(F.data.startswith("raper_list_"))
async def raper_list_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    page = int(callback.data.split("_")[-1]) if callback.data.startswith("raper_list_") else 0
    await raper_list(user_id=callback.from_user.id, page=page, state=state, bot=bot)


def paginate(items, current_page: int, items_per_page: int):
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    start = current_page * items_per_page
    end = start + items_per_page
    current_items = items[start:end]
    return current_items, total_pages


######## ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЕ ТРЕКОВ ########
@get_values.callback_query(F.data.startswith("tracks_list_"))
async def tracks_list(callback: CallbackQuery, state: FSMContext, bot: Bot):
    cds = callback.data.split("_")
    page = 0
    if len(cds) == 2:
        data = await state.get_data()
        raper_nick = data.get("raper_nick")
    elif len(cds) == 3:
        raper_nick = cds[2]
    else:
        raper_nick = cds[2]
        page = int(cds[-1])
    await state.clear()
    print(cds)  # ['tracks', 'list', '1']
    print(raper_nick)  # 1

    if not raper_nick:
        await bot.send_message(callback.from_user.id, "Барои ин рэпер трекҳо дар база нест!",
                               reply_markup=add_track_keyboard(raper_nick))
        return

    tracks = await get_tracks_by_raper_name(raper_nick)

    print(tracks)  # []

    if tracks:
        current_tracks, total_pages = paginate(tracks, page, ITEMS_PER_PAGE)
        tracks_str = "\n".join([f"{track.track_name} - {track.links}" for track in current_tracks])
        await bot.send_message(callback.from_user.id, f"<b>Трекҳои рэпер, {raper_nick}</b>:\n{tracks_str}\n",
                                          reply_markup=get_pagination_keyboard(page, total_pages, "tracks", raper_nick))
    else:
        await bot.send_message(callback.from_user.id, f"Ба рэпер <b>{raper_nick}</b> ҳоло трек ворид нашудааст!",
                               reply_markup=add_track_keyboard(raper_nick))
