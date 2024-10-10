from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu():
    keyboard = InlineKeyboardBuilder()

    instruction = InlineKeyboardButton(
        text="Получить инструкцию по настройке",
        callback_data="vpn_manual"
    )
    keyboard.add(instruction)

    json_configs = InlineKeyboardButton(
        text="Получить файлы для сервисов",
        callback_data="vpn_configs"
    )
    keyboard.add(json_configs)

    key_managment = InlineKeyboardButton(
        text="Управление ключами",
        callback_data="vpn_manage"
    )
    keyboard.add(key_managment)

    return keyboard.adjust(1).as_markup()


def manual_kb():
    keyboard = InlineKeyboardBuilder()
    app_android = InlineKeyboardButton(
        text="Скачать приложение для Android",
        url="https://play.google.com/store/apps/details?id=org.amnezia.vpn"
    )
    
    app_ios = InlineKeyboardButton(
        text="Скачать приложение для IOS",
        url="https://apps.apple.com/us/app/amneziavpn/id1600529900"
    )

    back = InlineKeyboardButton(
        text = "Назад",
        callback_data="vpn_back" 
    )

    keyboard.add(app_android)
    keyboard.add(app_ios) 
    keyboard.add(back)
    return keyboard.adjust(1).as_markup()


def configs_kb(configs):
    keyboard = InlineKeyboardBuilder()
    for config in configs:
        print(config)
        button = InlineKeyboardButton(
            text=str(config),
            callback_data="vpn_conf_"+str(config)
        )
        keyboard.add(button)

    back = InlineKeyboardButton(
        text = "Назад",
        callback_data="vpn_back" 
    )
    keyboard.add(back)

    return keyboard.adjust(1).as_markup()


def back():
    keyboard = InlineKeyboardBuilder()
    back = InlineKeyboardButton(
        text = "Назад",
        callback_data="vpn_back" 
    )
    keyboard.add(back)

    return keyboard.as_markup()


def manage_menu(flag: bool):
    keyboard = InlineKeyboardBuilder()

    new_key = InlineKeyboardButton(
        text="Запросить новый ключ",
        callback_data="vpn_ney_key"
    )
    keyboard.add(new_key)

    if flag:
        old_key = InlineKeyboardButton(
            text="Узнать свой ключ",
            callback_data="vpn_old_key"
        )
        keyboard.add(old_key)

    back = InlineKeyboardButton(
        text="Назад",
        callback_data="vpn_main_menu"
    )
    keyboard.add(back)

    return keyboard.adjust(1).as_markup()