import asyncio
import logging
import configparser

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from handlers_bank import main_router, admin_router, vpn_router

from db import db

config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('BOT', 'TOKEN')

bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )


async def main():
    session = await db.create_async_session()
    main_router.session = session
    admin_router.session = session
    vpn_router.session = session


    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(main_router.main_router, admin_router.admin_router, vpn_router.vpn_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()) 


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())