from aiogram.types import Message, FSInputFile, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command, CommandStart
from lexicon.lexicon import LEXICON_RU
import os
from aiogram import Router, F
from WB_API.merge import stock_process, orders_process
from keyboards.inline_keyboards import keyboard_Ozon, keyboard_WB, keyboard_start

# Инициализируем роутер уровня модуля
router = Router()

# Этот хендлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    # button1 = KeyboardButton(text='/stock')
    # button2 = KeyboardButton(text='/orders')
    # button3 = KeyboardButton(text='/WhoIsOrta')
    # keyboard = ReplyKeyboardMarkup(keyboard=[[button1, button2, button3]], resize_keyboard=True, one_time_keyboard=True)
    await message.answer(text=LEXICON_RU['/start'], reply_markup=keyboard_start)

# Этот хендлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

# Этот хендлер срабатывает на команду /stock
@router.message(F.text=='/stock')
async def process_stock_command(message: Message):
    data = stock_process()
    await message.answer(text=LEXICON_RU['/stock'])
    doc_path = os.path.join(os.path.dirname(__file__), '..', 'WB_API', 'file.xlsx')
    doc = FSInputFile(doc_path)
    await message.reply_document(document=doc)

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery WB
@router.callback_query(F.data=='Wildberries')
async def process_callback_command_WB(callback: CallbackQuery):
    await callback.message.edit_text(text="Wildberries", reply_markup=keyboard_WB)

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery Ozon
@router.callback_query(F.data=='Ozon')
async def process_callback_command_Ozon(callback: CallbackQuery):
    await callback.message.edit_text(text="Ozon", reply_markup=keyboard_Ozon)

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery Ozon
@router.callback_query(F.data=='Back')
async def process_callback_command_back(callback: CallbackQuery):
    await callback.message.edit_text(text="Выбери площадку", reply_markup=keyboard_start)

# Этот хендлер срабатывает на команду /orders
@router.message(F.text=='/orders')
async def process_orders_command(message: Message):
    data = orders_process()
    await message.answer(text=LEXICON_RU['/orders'])
    img_path = os.path.join(os.path.dirname(__file__), '..', 'WB_API', 'sales_by_date.png')
    img = FSInputFile(img_path)
    await message.reply_photo(photo=img)

# Этот хендлер срабатывает на команду /WhoIsOrta
@router.message(F.text=='/WhoIsOrta')
async def process_who_command(message: Message):
    img_path = os.path.join(os.path.dirname(__file__), 'who.png')
    img = FSInputFile(img_path)
    await message.reply_photo(photo=img)

# Этот хендлер срабатывает на остальные сообщения
@router.message()
async def process_other_message(message: Message):
    await message.answer(text=LEXICON_RU['no_echo'])