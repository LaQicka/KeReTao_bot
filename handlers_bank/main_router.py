from aiogram import Router, F, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery 
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import configparser

from keyboard_bank import main_kb, admin_kb
from states import UserState

from db import db
import util

config = configparser.ConfigParser()
config.read('config.ini')

main_router = Router()
session = None


@main_router.message(Command("start"))
async def start(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    try:
        users = await db.get_all_krt_users(session)
        
        reg = True
        for user in users:
            if user_id == user.user_id:
                reply_markup = None
                if user_id == int(config.get('BOT', 'ADMIN_ID')):
                    reply_markup = main_kb.main_keyboard_with_admin
                else:
                    reply_markup = main_kb.main_keyboard
        
                await msg.answer(text= "Проверка регистрации успешна.\nПриятного пользования сервисами UnitedMordor",
                            reply_markup=reply_markup)
                await state.set_state(UserState.in_system)
                break
        else:
            await state.update_data(current_state="registration")
            await msg.answer(text= "Добро пожаловать.\nДля доступа к сервисам требуется регистрация",
                            reply_markup = main_kb.registration_kb())
    except:
        await msg.answer(text= "ПРОИЗОШЛА ОШИБКА")
        
            

# ===== Обработка регистрации пользователя в системе =====

@main_router.callback_query(F.data == "registration")
async def registration_start(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.registration)
    await clbck.bot.edit_message_text(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        text="Напишите сопроводительное сообщение для администратора")


@main_router.message(UserState.registration)
async def proceed_registration(message: Message, state: FSMContext, bot: Bot):
    user_first_name = message.from_user.first_name
    user_last_name = message.from_user.last_name

    try:
        await db.create_krt_reg_request(session, message.from_user.id, str(user_first_name) + " " + str(user_last_name), message.text)
        
        await message.answer("Ваша заявка отправлена на рассмотрение")
        await state.set_state(UserState.in_system)
    except:
        await message.answer("ОШИБКА. Попробуйте еще раз")

# =====  =====