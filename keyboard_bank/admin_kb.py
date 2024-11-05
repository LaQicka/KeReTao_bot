from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


back_button = InlineKeyboardButton(
    text="НАЗАД",
    callback_data="admin_menu" 
)

def admin_menu():
    keyboard = InlineKeyboardBuilder()
    reg_requests_button = InlineKeyboardButton(
        text="Список заявок в KeReTao",
        callback_data="admin_krt_requests"
    )

    vpn_requests_button = InlineKeyboardButton(
        text="Список заявок на vpn ключ",
        callback_data="admin_vpn_requests"
    )

    send_message_button = InlineKeyboardButton(
        text="Сделать объявление",
        callback_data="admin_send_msg"
    )

    keyboard.add(reg_requests_button)
    keyboard.add(vpn_requests_button)
    keyboard.add(send_message_button)

    return keyboard.adjust(1).as_markup()


def requests_menu(requests):
    keyboard = InlineKeyboardBuilder()
    for req in requests:
        button = InlineKeyboardButton(
            text=str(req.reg_msg),
            callback_data="req_"+str(req.user_id)
        )
        keyboard.add(button)
    
    keyboard.add(back_button)

    return keyboard.adjust(1).as_markup()
    

def registration_approve_kb(request):
    keyboard = InlineKeyboardBuilder()
    approve_reg = InlineKeyboardButton(
        text="Принять заявку пользователя",
        callback_data="a_reg_approve_" + str(request.user_id)
    )
    decline_reg = InlineKeyboardButton(
        text="Отклонить заявку пользователя",
        callback_data="a_reg_decline_" + str(request.user_id)
    )
    
    keyboard.add(approve_reg)
    keyboard.add(decline_reg)
    keyboard.add(back_button)

    return keyboard.adjust(1).as_markup()


def admin_msg_kb():
    keyboard = InlineKeyboardBuilder()
    approve_msg = InlineKeyboardButton(
        text="Отправить объявление",
        callback_data="admin_send_msg_approve"
    )
    decline_msg = InlineKeyboardButton(
        text="Отменить отправку объявления",
        callback_data="admin_send_msg_decline"
    )
    keyboard.add(approve_msg)
    keyboard.add(decline_msg)
    return keyboard.adjust(1).as_markup()




def vpn_requests_menu(requests):
    keyboard = InlineKeyboardBuilder()
    for req in requests:
        button = InlineKeyboardButton(
            text=str(req.username),
            callback_data="a_vpn_list_"+str(req.user_id)
        )
        keyboard.add(button)
    
    keyboard.add(back_button)
    return keyboard.adjust(1).as_markup()
    

def vpn_reg_approve_kb(request):
    keyboard = InlineKeyboardBuilder()
    approve_reg = InlineKeyboardButton(
        text="Принять заявку пользователя",
        callback_data="a_vpn_ok_" + str(request.user_id)
    )
    decline_reg = InlineKeyboardButton(
        text="Отклонить заявку пользователя",
        callback_data="a_vpn_not_" + str(request.user_id)
    )
    keyboard.add(approve_reg)
    keyboard.add(decline_reg)
    keyboard.add(back_button)
    return keyboard.adjust(1).as_markup()


def vpn_keys_list_kb(keys):
    keyboard = InlineKeyboardBuilder()
    for key in keys:
        button = InlineKeyboardButton(
            text=str(key.key_caption),
            callback_data="vpn_key_"+str(key.id)
        )
        keyboard.add(button)

    keyboard.add(back_button)
    return keyboard.adjust(1).as_markup()