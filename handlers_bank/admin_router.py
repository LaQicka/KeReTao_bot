from aiogram import Router, F, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery 
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import configparser

from keyboard_bank import admin_kb, main_kb
from states import AdminState
from db import db
import util
from handlers_bank.main_router import session

config = configparser.ConfigParser()
config.read('config.ini')

admin_router=Router()
session = None

@admin_router.message(Command("admin"))
async def admin_menu(msg: Message):
    await msg.answer(
        text="Система KeReTao. Меню капитана",
        reply_markup=admin_kb.admin_menu()
    )


@admin_router.callback_query(F.data == "admin_menu")
async def admin_menu_clbck(clbck: CallbackQuery, state: FSMContext):
    await clbck.bot.edit_message_text(
        text="Система KeReTao. Меню капитана",
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        reply_markup=admin_kb.admin_menu()
    )


# ===== Обработка регистрационных заявок =====
@admin_router.callback_query(F.data == "admin_krt_requests")
async def krt_requests(clbck: CallbackQuery, state: FSMContext):
    requests = await db.get_all_krt_reg_requests(session)
    await clbck.bot.edit_message_text(
        text="Список активных заявок",
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        reply_markup=admin_kb.requests_menu(requests)
    )
    await clbck.answer()


@admin_router.callback_query(F.data.startswith("req_"))
async def show_req(clbck: CallbackQuery, state: FSMContext):
    user_id = int(clbck.data.split('_')[1])
    requests = await db.get_all_krt_reg_requests(session)
    request = None
    for req in requests:
        if int(req.user_id) == user_id:
            request = req

    if request == None:
        await clbck.answer()
        return 

    text = "USERNAME: " + request.username + '\n' + 'USER ID: ' + str(user_id) + '\n' + "REGISTRATION MESSAGE: " + request.reg_msg + '\n'
    await clbck.bot.edit_message_text(
        text=text,
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        reply_markup=admin_kb.registration_approve_kb(request)
    )
    await clbck.answer()   


@admin_router.callback_query(F.data.startswith("a_reg_approve_"))
async def admin_reg_approve(clbck: CallbackQuery, state: FSMContext):
    user_id = int(clbck.data.split('_')[3])
    request = await db.get_krt_reg_request_by_user_id(session, user_id)

    if request == None:
        await clbck.answer()
        return
    
    await db.create_krt_user(session, user_id, request.username)
    await db.delete_krt_request(session, request)
    
    await clbck.bot.send_message(
        chat_id=user_id,
        text="Ваша заявка в систему KeReTao одобрена",
        reply_markup=main_kb.main_keyboard
    )

    await clbck.answer(text="Пользователь добавлен в систему")

    await clbck.bot.edit_message_reply_markup(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        reply_markup=admin_kb.admin_menu()
    )


@admin_router.callback_query(F.data.startswith("a_reg_decline_"))
async def admin_reg_approve(clbck: CallbackQuery, state: FSMContext):
    user_id = int(clbck.data.split('_')[3])
    request = await db.get_krt_reg_request_by_user_id(session, user_id)

    if request == None:
        await clbck.answer()
        return 
    
    await db.delete_krt_request(session, request)
    
    await clbck.bot.send_message(
        chat_id=user_id,
        text="Ваша заявка в систему KeReTao отклонена",
        reply_markup=main_kb.main_keyboard
    )

    await clbck.answer(text="Заявка отклонена")

    await clbck.bot.edit_message_reply_markup(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        reply_markup=admin_kb.admin_menu()
    )




# ===== Обработка меню менеджмента VPN =====
@admin_router.callback_query(F.data == "admin_vpn_requests")
async def vpn_requests(clbck: CallbackQuery, state: FSMContext):
    requests = await db.get_all_vpn_key_requests(session)
    await clbck.bot.edit_message_text(
        text="Список запросов ключей",
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        reply_markup=admin_kb.vpn_requests_menu(requests)
    )
    await clbck.answer()


@admin_router.callback_query(F.data.startswith("a_vpn_list_"))
async def show_vpn_req(clbck: CallbackQuery, state: FSMContext):
    user_id = int(clbck.data.split('_')[3])
    request = await db.get_vpn_request_by_user_id(session, user_id)

    if request == None:
        await clbck.answer()
        return 

    text = "USERNAME: " + request.username + '\n' + 'USER ID: ' + str(user_id) + '\n'
    await clbck.bot.edit_message_text(
        text=text,
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        reply_markup=admin_kb.vpn_reg_approve_kb(request)
    )
    await clbck.answer()   


@admin_router.callback_query(F.data.startswith("a_vpn_ok_"))
async def vpn_reg_approve(clbck: CallbackQuery, state: FSMContext):
    user_id = int(clbck.data.split('_')[3])
    request = await db.get_vpn_request_by_user_id(session, user_id)

    if request == None:
        await clbck.bot.edit_message_text(
            chat_id=clbck.message.chat.id,
            message_id=clbck.message.message_id,
            text="ОШИБКА. ЗАЯВКА НЕ НАЙДЕНА")
        return 
    
    keys = await db.get_unused_vpn_keys(session, 5)
    # keys2 = await db.get_unused_vpn_keys(session, 0)
    # for k in keys2:
    #     print(k.key_caption)


    # await state.set_state(AdminState.vpn_key_waiting)
    await state.update_data({'user_id': user_id})
    await clbck.bot.edit_message_text(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        text="Выберите ключ для передачи",
        reply_markup=admin_kb.vpn_keys_list_kb(keys))
    

@admin_router.callback_query(F.data.startswith("a_vpn_not_"))
async def vpn_reg_deny(clbck: CallbackQuery):
    user_id = int(clbck.data.split('_')[3])
    request = await db.get_vpn_request_by_user_id(session, user_id)
    if request == None:
        await clbck.bot.edit_message_text(
            chat_id=clbck.message.chat.id,
            message_id=clbck.message.message_id,
            text="ОШИБКА. ЗАЯВКА НЕ НАЙДЕНА")
        return 
    await clbck.answer()
    await db.delete_vpn_request(session, request)
    

@admin_router.callback_query(F.data.startswith("vpn_key_"))
async def vpn_key_proceed(clbck: CallbackQuery, state: FSMContext, bot: Bot):
    id = int(clbck.data.split('_')[2])
    key = await db.get_vpn_key_by_id(session, id)
    user_data = await state.get_data()
    user_id = user_data['user_id']
    krt_user = await db.get_krt_user_by_user_id(session, user_id)

    await bot.send_message(
        chat_id=user_id,
        text="Ваш ключ для подключения:\n\n"
            + "`" + key.key + "`" + "\n\n"
            "Инструкции по подключению можно найти в разделе /vpn \n\n",
        parse_mode="MarkdownV2"

    )    
    await clbck.answer("Ключ отправлен пользователю")

    await db.update_vpn_key(session, id, krt_user.username, user_id, True)

    vpn_user = await db.get_vpn_user_by_user_id(session, user_id)
    request = await db.get_vpn_request_by_user_id(session, user_id)
    if vpn_user == None:
        await db.create_vpn_user(session, user_id, True, key)
    else:
        await db.update_vpn_user(session, user_id, key.key)

    await db.delete_vpn_request(session, request)


@admin_router.message(AdminState.vpn_key_waiting)
async def proceed_key(message: Message, state: FSMContext, bot: Bot):
    key = message.text
    user_data = await state.get_data()
    user_id = user_data['user_id']

    await bot.send_message(
        chat_id=user_id,
        text="Ваш ключ для подключения:\n\n"
            + "`" + key + "`" + "\n\n"
            "Инструкции по подключению можно найти в разделе /vpn \n\n",
        parse_mode="MarkdownV2"

    )    
    await message.answer("Ключ отправлен пользователю")

    vpn_user = await db.get_vpn_user_by_user_id(session, user_id)
    request = await db.get_vpn_request_by_user_id(session, user_id)
    if vpn_user == None:
        await db.create_vpn_user(session, user_id, True, key)
    else:
        await db.update_vpn_user(session, user_id, key)

    await db.delete_vpn_request(session, request)
    await state.set_state(AdminState.normal)
