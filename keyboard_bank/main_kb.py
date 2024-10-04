from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_keyboard_with_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/start"), KeyboardButton(text="/vpn"), KeyboardButton(text="/admin")]
], resize_keyboard=True)


main_keyboard= ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/start"), KeyboardButton(text="/vpn")]
], resize_keyboard=True)


def registration_kb():
    keyboard = InlineKeyboardBuilder()
    button_registration = InlineKeyboardButton(
        text="Создать запрос на регистрацию",
        callback_data="registration"
    )
    keyboard.add(button_registration)

    return keyboard.as_markup()


