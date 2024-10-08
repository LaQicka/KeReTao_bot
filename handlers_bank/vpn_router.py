from aiogram import Router, F, Bot, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery 
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from keyboard_bank import vpn_kb
from db import db
import util

vpn_router = Router()
session = None


@vpn_router.message(Command("vpn"))
async def main_menu(msg: Message):
    try:
        user = await db.get_krt_user_by_user_id(session, msg.from_user.id)
        if user:
            await msg.answer(
                text="Меню VPN",
                reply_markup=vpn_kb.main_menu()
            )
        else:
            await msg.answer(
                text="!!! В доступе отказано !!!"
            )
    except:
        await msg.answer(
                text="!!! ОШИБКА STOP 00000 !!!"
            )

@vpn_router.callback_query(F.data == "vpn_main_menu")
async def main_menu_clbck(clbck: CallbackQuery):
    await clbck.bot.edit_message_text(
        text="Меню VPN",
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        reply_markup=vpn_kb.main_menu()
    )


@vpn_router.callback_query(F.data == "vpn_back")
async def vpn_back_clbck(clbck: CallbackQuery):
    print("something done")
    await clbck.bot.delete_message(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id
    )
    
    await clbck.bot.send_message(
        text="Меню VPN",
        chat_id=clbck.message.chat.id,
        reply_markup=vpn_kb.main_menu()
    )



@vpn_router.callback_query(F.data == "vpn_manual")
async def manual(clbck: CallbackQuery):
    media = types.FSInputFile(path = 'media/MANUAL_ANDROID.mp4')
    
    await clbck.bot.delete_message(
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id
    )

    await clbck.bot.send_video(
        caption="Скачайте приложение по ссылке и следуйте видеоинструкции.\n\n" + 
                "Отключать VPN нет необходимости, он будет работать только в выбранных приложениях.\n\n" + 
                "По аналогии с YouTube можно добавить другие сервисы в список.\n",
        chat_id=clbck.message.chat.id,
        video=media,
        reply_markup=vpn_kb.manual_kb()
    )
    await clbck.answer()


@vpn_router.callback_query(F.data == "vpn_manage")
async def manage_menu(clbck: CallbackQuery,  state: FSMContext):
    try:
        user = await db.get_vpn_user_by_user_id(session, clbck.from_user.id)
    except:
        print("ERROR OCCURED")
        await clbck.answer()
        return

    if user and user.reg == True:
        await clbck.bot.edit_message_text(
            text="Выберите действие с ключами",
            chat_id=clbck.message.chat.id,
            message_id=clbck.message.message_id,
            reply_markup=vpn_kb.manage_menu(True)
        )
    
    else:
        await clbck.bot.edit_message_text(
            text="Выберите действие с ключами",
            chat_id=clbck.message.chat.id,
            message_id=clbck.message.message_id,
            reply_markup=vpn_kb.manage_menu(False)
        )

    await clbck.answer()


@vpn_router.callback_query(F.data == "vpn_ney_key")
async def ask_ney_key(clbck: CallbackQuery,  state: FSMContext, bot: Bot):

    await clbck.bot.send_message(
        chat_id=clbck.message.chat.id,
        text="Ваша заявка отправлена. Вскоре вам выделят ключ"
    )
    await bot.delete_message(clbck.message.chat.id, clbck.message.message_id)

    try:
        await db.create_vpn_key_request(session, clbck.from_user.id, str(clbck.from_user.first_name) + " " + str(clbck.from_user.last_name))
    except:
        print("ERROR OCCURED")
        await clbck.answer()
        return

    await clbck.answer()

    
@vpn_router.callback_query(F.data == "vpn_old_key")
async def ask_old_key(clbck: CallbackQuery,  state: FSMContext):
    
    try:
        user = await db.get_vpn_user_by_user_id(session, clbck.from_user.id)
        
        if user:
            await clbck.bot.send_message(
                chat_id=clbck.message.chat.id,
                text=user.key
            )   
        else:
            await clbck.answer("USER UNKNOW")
            return 
    except:
        await clbck.answer("USER UNKNOW")
        return

    await clbck.answer()
