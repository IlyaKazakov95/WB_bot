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
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from WB_API.ozon_orders_extract import ozon_extract_orders
from WB_API.wb_stock_history import stock_history_extract
from WB_API.wb_unite_stock_orders import wb_stock_orders_unite
from WB_API.merge import union_sales

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

    # создаём планировщик для asyncio
    scheduler = AsyncIOScheduler(timezone=timezone("Europe/Moscow"))

    # добавляем задачу: каждый день в 05:00 по Москве
    scheduler.add_job(ozon_extract_orders, 'cron', hour=5, minute=0)
    scheduler.add_job(union_sales, 'cron', hour=5, minute=10)
    scheduler.add_job(stock_history_extract, 'cron', hour=5, minute=20)
    scheduler.add_job(wb_stock_orders_unite, 'cron', hour=5, minute=35)

    # запускаем планировщик
    scheduler.start()

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