from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_button(text: str, callback_data: str = None, url: str = None) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data, url=url)

def create_inline_keyboard(buttons: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=buttons)

raper_list_btn = create_button("📃 Рӯйхати рэперҳо 👥🎙️", "raper_list")
search_btn = create_button("Ҷустуҷуи рэпер 🔎🙋🎤", "search")
random_btn = create_button("Рэпери тасодуфӣ 🎤✨", "random")
latest_btn = create_button("Рэпери охир воридшуда", "latest")
info_btn = create_button("ℹ️🔊 Маълумот оиди рэпер", "info_about_raper")
add_raper_btn = create_button("Рэпери нав ворид кардан", "add_raper")
site_btn = create_button("🕸 сайти RAP TJ 🎤🎧🇹🇯", url="https://www.youtube.com/@rapportal")
help_btn = create_button("Кумак 🆘", "help")

def raper_tracks_btn(raper_nick: str) -> InlineKeyboardButton:
    return create_button("Трекҳои рэпер 🔊🎤👨‍🎤", f"tracks_list_{raper_nick}")

def add_track_btn(raper_nick: str) -> InlineKeyboardButton:
    return create_button("Треки нав ворид кардан", f"add_track_{raper_nick}")

start_keyboard = create_inline_keyboard([
    [raper_list_btn, search_btn],
    [random_btn, latest_btn],
    [site_btn, help_btn]])

raper_list_keyboard = create_inline_keyboard([[search_btn], [random_btn], [latest_btn]])
add_raper_keyboard = create_inline_keyboard([[add_raper_btn]])
what_else_keyboard = create_inline_keyboard([[info_btn], [search_btn, raper_list_btn]])
unit_raper_list_keyboard = create_inline_keyboard([[search_btn, add_raper_btn], [info_btn, random_btn]])
open_site_keyboard = create_inline_keyboard([[site_btn]])

def raper_tracks_keyboard(raper_nick: str) -> InlineKeyboardMarkup:
    return create_inline_keyboard([[raper_tracks_btn(raper_nick)]])

def add_track_keyboard(raper_nick: str) -> InlineKeyboardMarkup:
    return create_inline_keyboard([[add_track_btn(raper_nick)]])

def after_adding_raper_keyboard(raper_nick: str) -> InlineKeyboardMarkup:
    return create_inline_keyboard([
        [add_track_btn(raper_nick), add_raper_btn],
        [info_btn, raper_list_btn]])

def raper_found_keyboard(raper_nick: str) -> InlineKeyboardMarkup:
    return create_inline_keyboard([[info_btn],
        [raper_tracks_btn(raper_nick)],
        [add_track_btn(raper_nick)]])


def get_pagination_keyboard(current_page: int, total_pages: int, item: str, raper_nick=None) -> InlineKeyboardMarkup:
    buttons = []
    nick = raper_nick + "_" if raper_nick else ""
    if current_page > 0:
        buttons.append([create_button("◀ Пас", f"{item}_list_{nick}{current_page - 1}")])

    if current_page < total_pages - 1:
        buttons.append([create_button("Давом ▶", f"{item}_list_{nick}{current_page + 1}")])

    additional_buttons = [search_btn, add_raper_btn]
    if raper_nick is not None:
        a = [add_track_btn(raper_nick)]
        buttons.extend([a])
    return create_inline_keyboard(buttons + [additional_buttons])
