import os
import asyncio
import aiohttp


from database.engine import drop_db, session_maker, create_db
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers.user_private import user_private_router


load_dotenv()

bot = Bot(token=os.getenv("TG_TOKEN"))
dp = Dispatcher()
dp.include_router(user_private_router)


async def on_startup():
    # await drop_db()
    await create_db()
    dp.http_session = aiohttp.ClientSession()

async def on_shutdown():
    await dp.http_session.close()
    await bot.session.close()


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)    

    try:
    #   await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
      await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
      dp.http_session = aiohttp.ClientSession()
    except KeyboardInterrupt:
        
        await bot.session.close()
        # await bot.close()
        print("bot dont active")


if __name__ == "__main__":
    asyncio.run(main())