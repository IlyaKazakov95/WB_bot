import asyncio
import logging
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from aiogram import Bot, Dispatcher
from config.config import Config, load_config
from handlers import user
from keyboards.set_menu import set_menu
from middlewares.outer import OuterMiddleware

async def main() -> None:
    # Загружаем конфиг в переменную config
    config: Config = load_config()
    # Задаём базовую конфигурацию логирования
    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format)
    # Инициализируем бот и диспетчер
    bot = Bot(token=config.bot.token)
    dp = Dispatcher()

    # Настраиваем кнопку меню
    await set_menu(bot)

    # Регистриуем роутеры в диспетчере
    dp.include_router(user.router)

    # Регистрируем миддлвари
    dp.update.outer_middleware(OuterMiddleware())

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())