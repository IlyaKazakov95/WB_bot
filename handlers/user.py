from aiogram.types import Message, FSInputFile, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command, CommandStart
from lexicon.lexicon import LEXICON_RU, LEXICON_PRODUCT_RU
import os
from aiogram import Router, F
from WB_API.merge import stock_process, orders_process
from keyboards.inline_keyboards import keyboard_Ozon, keyboard_WB, keyboard_start, create_inline_kb
from WB_API.ozon_graphics import ozon_order_graphics, ozon_order_graphics_by_sku
from WB_API.ozon_stock_extract import ozon_stock_extract
from middlewares.outer import user_dict

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

# Этот хендлер срабатывает на команду /WB_Orders
@router.callback_query(F.data=='/WB_Orders')
async def process_orders_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(sticker='CAACAgIAAxkBAAEBngNo0lwZQuecuOIvt415JZ0ugggatAAC6FoAAkdHeEkbUe10quf-QDYE')
    img_path = orders_process()[1]
    img = FSInputFile(img_path)
    await callback.message.answer(text=LEXICON_RU['/orders'])
    await callback.message.reply_photo(photo=img)
    await callback.message.answer(text="Wildberries", reply_markup=keyboard_WB)

# Этот хендлер срабатывает на команду /WB_Stock
@router.callback_query(F.data=='/WB_Stock')
async def process_stock_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(
        sticker='CAACAgIAAxkBAAEBngFo0lwOMe8IR3M3xcCiVB9h67hAXAACZ2IAAmsxeEn1NiNpBuDibDYE')
    doc_path = stock_process()
    doc = FSInputFile(doc_path)
    await callback.message.answer(text=LEXICON_RU['/stock'])
    await callback.message.reply_document(document=doc)
    await callback.message.answer(text="Wildberries", reply_markup=keyboard_WB)

# Этот хендлер срабатывает на команду /Ozon_Orders
@router.callback_query(F.data=='/Ozon_Orders')
async def process_ozon_orders_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(
        sticker='CAACAgIAAxkBAAEBngVo0l7RHB6WPJJjwF-FEkzfQioDLQACZF8AAiAMeEm-gIMfjPJM9zYE')
    img_path = ozon_order_graphics()
    img = FSInputFile(img_path)
    await callback.message.answer(text=LEXICON_RU['/orders'])
    await callback.message.reply_photo(photo=img)
    kb = create_inline_kb(width=1, **LEXICON_PRODUCT_RU)
    await callback.message.answer(text="Можно посмотреть детальнее по sku", reply_markup=kb)

# Этот хендлер срабатывает на команды по баркодам
@router.callback_query(lambda x: x.data.isdigit() and (len(x.data)==10 or len(x.data)==9))
async def process_ozon_orders_by_sku_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(
        sticker='CAACAgIAAxkBAAEBngVo0l7RHB6WPJJjwF-FEkzfQioDLQACZF8AAiAMeEm-gIMfjPJM9zYE')
    img_path = ozon_order_graphics_by_sku(filter=str(callback.data))
    img = FSInputFile(img_path)
    await callback.message.answer(text=LEXICON_RU['/orders'])
    await callback.message.reply_photo(photo=img)
    await callback.message.answer(text="Можно посмотреть детальнее по sku", reply_markup=keyboard_Ozon)

# Этот хендлер срабатывает на команду /Ozon_Stock
@router.callback_query(F.data=='/Ozon_Stock')
async def process_ozon_stock_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(
        sticker='CAACAgIAAxkBAAEBnglo0l9kI8plUYwJt75T0DCM-7ySTQACSGoAAt7oeUnaJPE98T9j_jYE')
    data = ozon_stock_extract()
    doc_path = os.path.join(os.path.dirname(__file__), '..', 'WB_API', 'ozon_stock.xlsx')
    doc = FSInputFile(doc_path)
    await callback.message.answer(text=LEXICON_RU['/stock'])
    await callback.message.reply_document(document=doc)
    await callback.message.answer(text="Ozon", reply_markup=keyboard_Ozon)

# Этот хендлер срабатывает на команду /WhoIsOrta
@router.message(F.text=='/WhoIsOrta')
async def process_who_command(message: Message):
    img_path = os.path.join(os.path.dirname(__file__), 'who.png')
    img = FSInputFile(img_path)
    await message.reply_photo(photo=img)

# Этот хендлер срабатывает на команду /stat
@router.message(F.text == '/stat')
async def process_stat_command(message: Message):
    if not user_dict:
        await message.answer("Нет данных о пользователях.")
        return

    text = "📊 Статистика:\n\n"
    for uid, db in user_dict.items():
        text += (
            f"👤 {db.username}\n"
            f"Запросов: {db.requests_qty}\n"
            f"Последний: {db.last_requests_date}\n\n"
        )

    await message.answer(text)

# Этот хендлер срабатывает на остальные сообщения
@router.message()
async def process_other_message(message: Message):
    await message.answer(text=LEXICON_RU['no_echo'])