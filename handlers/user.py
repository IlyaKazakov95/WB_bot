from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from lexicon.lexicon import LEXICON_RU
import os

img_path = os.path.join(os.path.dirname(__file__), '..', 'WB_API', 'sales_by_date.png')
doc_path = os.path.join(os.path.dirname(__file__), '..', 'WB_API', 'file.xlsx')

# Этот хендлер срабатывает на команду /start
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'])

# Этот хендлер срабатывает на команду /help
@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

# Этот хендлер срабатывает на команду /stock
@dp.message(Command(commands='stock'))
async def process_stock_command(message: Message):
    await message.answer(text=LEXICON_RU['/stock'])
    await message.reply_document(document=open(doc_path, 'rb'))

# Этот хендлер срабатывает на команду /orders
@dp.message(Command(commands='orders'))
async def process_stock_command(message: Message):
    await message.answer(text=LEXICON_RU['/orders'])
    await message.reply_photo(photo=open(img_path, 'rb'))

# Этот хендлер срабатывает на остальные сообщения
@dp.message()
async def process_other_message(message: Message):
    await message.answer(text=LEXICON_RU['no_echo'])

