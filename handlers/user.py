from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from lexicon.lexicon import LEXICON_RU
import os
from aiogram import Router
from WB_API.merge import stock_process, orders_process

# Инициализируем роутер уровня модуля
router = Router()

img_path = os.path.join(os.path.dirname(__file__), '..', 'WB_API', 'sales_by_date.png')
doc_path = os.path.join(os.path.dirname(__file__), '..', 'WB_API', 'file.xlsx')

# Этот хендлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'])

# Этот хендлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

# Этот хендлер срабатывает на команду /stock
@router.message(Command(commands='stock'))
async def process_stock_command(message: Message):
    data = stock_process()
    await message.answer(text=LEXICON_RU['/stock'])
    await message.reply_document(document=open(doc_path, 'rb'))

# Этот хендлер срабатывает на команду /orders
@router.message(Command(commands='orders'))
async def process_orders_command(message: Message):
    data = orders_process()
    await message.answer(text=LEXICON_RU['/orders'])
    await message.reply_photo(photo=open(img_path, 'rb'))

# Этот хендлер срабатывает на остальные сообщения
@router.message()
async def process_other_message(message: Message):
    await message.answer(text=LEXICON_RU['no_echo'])

