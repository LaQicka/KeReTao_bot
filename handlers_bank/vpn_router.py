import os

from aiogram import Router, F, Bot, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from keyboard_bank import vpn_kb
from db import db

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
                text="!!! ОШИБКА STOP 00000 !!! (Попробуйте еще разок)"
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


@vpn_router.callback_query(F.data == "vpn_configs")
async def vpn_configs(clbck: CallbackQuery):
    media_dir = os.path.join(os.getcwd(), 'media/vpn_jsons')
    json_files = [os.path.splitext(f)[0] for f in os.listdir(media_dir) if f.endswith('.json')]
    
    text = "Вот конфиги для сервисов, которые вы можете использовать для раздельного туннелирования сайтов.\n\n\n"
    text += "Вскоре будет инструкция по их подключению, пока просто скажу - чтобы добавить их нужно зайти в \n\n"
    text += "split tunneling  --> \nsite-based split tunneling --> \nВ правом нижнем углу 3 точки --> \nImport --> \nAdd imported sites to existing ones\n\n"
    text += "Для каждого сайта нужно добавлять отдельные файлы. Например для youtube файл называется youtube.json"


    await clbck.bot.edit_message_text(
        text=text,
        chat_id=clbck.message.chat.id,
        message_id=clbck.message.message_id,
        reply_markup=vpn_kb.configs_kb(json_files)
    )

    await clbck.answer()

@vpn_router.callback_query(F.data.startswith("vpn_conf_"))
async def send_config(clbck: CallbackQuery):
    filename = clbck.data.split('_')[2]
    filepath = os.path.join(os.getcwd(), 'media/vpn_jsons', filename + '.json')
    await clbck.answer()
    if os.path.exists(filepath):
        file = types.FSInputFile(filepath)
        await clbck.message.answer_document(file)
    else:
        await clbck.message.answer("Файл не найден.")


# ===== Обработка меню менеджмента ключей =====
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
        key_model = await db.get_vpn_key_by_id(session, user.key_id)

        if user:
            await clbck.bot.send_message(
                chat_id=clbck.message.chat.id,
                text=key_model.key
            )   
        else:
            await clbck.answer("USER UNKNOW")
            return 
    except:
        await clbck.answer("USER UNKNOW")
        return

    await clbck.answer()
