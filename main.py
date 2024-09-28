from asyncio import run
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import ClientSession
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from app.config import API_TOKEN
from app.database import reset_database
from app.get_values import get_values
from app.search import searching
from app.states import states
from app.keyboards import start_keyboard, open_site_keyboard

router = Router()
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()
dp.include_routers(searching, states, get_values)


@dp.message(CommandStart())
async def start(message: Message):
    start_text = """Салом!👋🏻\n Ман метавонам ба шумо маълумот оиди рэперҳо 🙋🎤 ва трекҳои онҳоро 🎶🎼 пешниҳод кунам\n
    Яке аз командаҳоро пахш намоед!"""
    await message.answer(start_text, reply_markup=start_keyboard)


async def open_site_async(url: str):
    async with ClientSession() as session:
        async with session.get(url) as response:
            return response.status == 200


@dp.message(Command("site"))
@dp.callback_query(F.data == "site")
async def site(callback: CallbackQuery):
    url = "https://www.youtube.com/@rapportal"
    await open_site_async(url)
    await bot.send_message(callback.from_user.id, "сайт кушода нашуда бошад тугмаи зерро зер кунед", reply_markup=open_site_keyboard)



@dp.message(Command("drop_db"))
async def drop_db(message: Message):
    await reset_database()
    await message.answer("База данных стёрта и пересозданна")


@dp.message(Command("help"))
@dp.callback_query(F.data == "help")
async def cmd_help(callback: CallbackQuery):
    await callback.bot.send_message(callback.from_user.id,
        """        Ман бот-еям ки барои ёфтани рэперҳо ва пешниҳод намудани трекҳои оно ба ту кумак мекунам

                Ман ана ин чизҳоро метонам:
        /start - Оғози кор бо бот
        /search {нoми рэпер} - Маълумот оиди рэпер ҷустан
        /random - Пешниҳоди рэпери тасодуфӣ
        /latest - Пешниҳоди рэпери охир ворид шуда
        /list - Руйхати ҳамаи реперҳоро нишон додан

        Агар рэпере ворид набошад /add_raper нависед ба дастурҳоро риоя кунед!

        Мисол, барои маълумот оиди "<b>Baron</b>" дарёфт кардан: /search-ро пахш намоедую никашро нависед""")


async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    run(main())
