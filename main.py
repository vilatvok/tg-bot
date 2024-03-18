import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import TOKEN
from middlewares import DbMiddleware
from database.engine import create_db, session_maker
from handlers.base import router
from handlers.profile import router as profile_router
from handlers.edit_profile import router as edit_profile_router
from handlers.admin import router as admin_router
from utils.bot_cmds import bot_cmds


async def on_startup(bot):
    await create_db()


async def main():
    dp = Dispatcher()

    dp.include_routers(router, profile_router, edit_profile_router, admin_router)
    dp.startup.register(on_startup)
    dp.update.middleware(DbMiddleware(session=session_maker))

    bot = Bot(token=TOKEN)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=bot_cmds)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())