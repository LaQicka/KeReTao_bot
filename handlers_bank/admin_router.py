from aiogram import Router, F, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery 
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import configparser

import handlers_bank
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


# ===== Отправки пользователям сообщения =====
@admin_router.callback_query(F.data == "admin_send_msg")
async def admin_send_msg(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.msg_wait)
    await clbck.bot.edit_message_text(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        text="Введите текст объявления")


@admin_router.message(AdminState.msg_wait)
async def proceed_msg(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(text = message.text)
    await bot.send_message(
        chat_id=message.chat.id,
        text = message.text,
        reply_markup=admin_kb.admin_msg_kb()    
    )    

@admin_router.callback_query(F.data == "admin_send_msg_approve")
async def proceed_msg_approve(clbck: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text")

    try:
        users = await db.get_all_krt_users(session)
        for user in users:
            await clbck.bot.send_message(
                text=text,
                chat_id=user.user_id
            )
    except:
        await clbck.answer("Ошибка отправки")


    await clbck.answer("Объявление отправлено")
    await state.clear()
    await state.set_state(AdminState.normal)
    await clbck.bot.delete_message(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id
    )


@admin_router.callback_query(F.data == "admin_send_msg_decline")
async def proceed_msg_approve(clbck: CallbackQuery, state: FSMContext):
    await clbck.answer("Отправка объявления отменена")
    await state.clear()
    await state.set_state(AdminState.normal)
    await clbck.bot.delete_message(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id
    )


# ===== Обработка регистрационных заявок =====
@admin_router.callback_query(F.data == "admin_krt_requests")
async def krt_requests(clbck: CallbackQuery, state: FSMContext):
    try:
        requests = await db.get_all_krt_reg_requests(session)
        await clbck.bot.edit_message_text(
            text="Список активных заявок",
            chat_id=clbck.message.chat.id,
            message_id=clbck.message.message_id,
            reply_markup=admin_kb.requests_menu(requests)
        )
        await clbck.answer()
    except:
        print("SOME ERROR OCCURED")
        await clbck.answer()


@admin_router.callback_query(F.data.startswith("req_"))
async def show_req(clbck: CallbackQuery, state: FSMContext):
    user_id = int(clbck.data.split('_')[1])

    try:
        requests = await db.get_all_krt_reg_requests(session)
    except:
        print("DB ERROR READ REQESTS")
        await clbck.answer()
        return
    
    request = None
    for req in requests:
        if int(req.user_id) == user_id:
            request = req

    if request == None:
        await clbck.answer()
        return 
    
    try: 
        username = "USERNAME: " + str(request.username)
    except:
        username = "USERNAME: EMPTY"

    user_id_str = "USER_ID: " + str(user_id)

    try: 
        reg_msg = "REGISTRATION MESSAGE: " + request.reg_msg
    except:
        reg_msg = "REGISTRATION MESSAGE: EMPTY_MSG"
    
    text = username + "\n" + user_id_str + "\n" + reg_msg + "\n"
    
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

    try:
        user = await db.get_krt_user_by_user_id(session, user_id)
        if user != None:
            print("User already in system")
            await clbck.answer()
            return
    except:
        print("DB ERROR READ USER")
        await clbck.answer()
        return

    try:
        request = await db.get_krt_reg_request_by_user_id(session, user_id)
    except:
        print("DB ERROR READ REQEST")
        await clbck.answer()
        return

    if request == None:
        await clbck.answer()
        return

    try:
        await db.create_krt_user(session, user_id, request.username)
        await db.delete_krt_request(session, request)
    except:
        print("DB ERROR CREATE KRT USER")
        await clbck.answer()
        return


    await clbck.bot.send_message(
        chat_id=user_id,
        text="Ваша заявка в систему KeReTao одобрена. Перезагрузите бота командой /start",
    )

    await clbck.answer(text="Пользователь добавлен в систему")

    await clbck.bot.edit_message_reply_markup(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        reply_markup=admin_kb.admin_menu()
    )


@admin_router.callback_query(F.data.startswith("a_reg_decline_"))
async def admin_reg_decline(clbck: CallbackQuery, state: FSMContext):
    user_id = int(clbck.data.split('_')[3])

    try:
        request = await db.get_krt_reg_request_by_user_id(session, user_id)
    except:
        print("DB ERROR READ REQEST")
        await clbck.answer()
        return

    if request == None:
        await clbck.answer()
        return 
    
    try:
        await db.delete_krt_request(session, request)
    except:
        print("DB ERROR DELETE REQEST")
        await clbck.answer()
        return
    

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

    try:
        requests = await db.get_all_vpn_key_requests(session)
    except:
        print("DB ERROR READ REQESTS")
        await clbck.answer()
        return
    
    
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
    
    try:
        request = await db.get_vpn_request_by_user_id(session, user_id)
    except:
        print("DB ERROR READ REQESTS")
        await clbck.answer()
        return

    if request == None:
        await clbck.answer()
        return 

    try: 
        username = "USERNAME: " + str(request.username)
    except:
        username = "USERNAME: EMPTY"


    text = username + '\n' + 'USER ID: ' + str(user_id) + '\n'
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
    
    try:    
        request = await db.get_vpn_request_by_user_id(session, user_id)
    except:
        print("DB ERROR READ REQESTS")
        await clbck.answer()
        return

    if request == None:
        await clbck.bot.edit_message_text(
            chat_id=clbck.message.chat.id,
            message_id=clbck.message.message_id,
            text="ОШИБКА. ЗАЯВКА НЕ НАЙДЕНА")
        return 
    
    try:
        keys = await db.get_unused_vpn_keys(session, 5)
    except:
        print("DB ERROR READ KEYS")
        await clbck.answer()
        return


    await state.update_data({'user_id': user_id})
    await clbck.bot.edit_message_text(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        text="Выберите ключ для передачи",
        reply_markup=admin_kb.vpn_keys_list_kb(keys))
    

@admin_router.callback_query(F.data.startswith("a_vpn_not_"))
async def vpn_reg_deny(clbck: CallbackQuery):
    user_id = int(clbck.data.split('_')[3])
    
    try:
        request = await db.get_vpn_request_by_user_id(session, user_id)
    except:
        print("DB ERROR READ REQEST")
        await clbck.answer()
        return

    if request == None:
        await clbck.bot.edit_message_text(
            chat_id=clbck.message.chat.id,
            message_id=clbck.message.message_id,
            text="ОШИБКА. ЗАЯВКА НЕ НАЙДЕНА")
        return 
    await clbck.answer()

    try:
        await db.delete_vpn_request(session, request)
    except:
        print("DB ERROR DELETING REQEST")
        await clbck.answer()
        return


@admin_router.callback_query(F.data.startswith("vpn_key_"))
async def vpn_key_proceed(clbck: CallbackQuery, state: FSMContext, bot: Bot):
    id = int(clbck.data.split('_')[2])
    user_data = await state.get_data()
    user_id = user_data['user_id']

    try:
        key = await db.get_vpn_key_by_id(session, id)
        krt_user = await db.get_krt_user_by_user_id(session, user_id)
    
        await bot.send_message(
            chat_id=user_id,
            text="Ваш ключ для подключения:\n\n"
                + "`" + str(key.key) + "`" + "\n\n"
                "Инструкции по подключению можно найти в разделе /vpn \n\n",
            parse_mode="MarkdownV2"

        )    
        await clbck.answer("Ключ отправлен пользователю")

        await db.update_vpn_key(session, id, krt_user.username, user_id, True)

        vpn_user = await db.get_vpn_user_by_user_id(session, user_id)
        request = await db.get_vpn_request_by_user_id(session, user_id)
    
        if vpn_user == None:
            await db.create_vpn_user(session, user_id, True, key.key)
        else:
            await db.update_vpn_user(session, user_id, key.key)

        await db.delete_vpn_request(session, request)
        
    except:
        print("DB ERROR")
        return
