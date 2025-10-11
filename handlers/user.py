from aiogram.types import Message, FSInputFile, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command, CommandStart
from lexicon.lexicon import LEXICON_RU, LEXICON_PRODUCT_RU, LEXICON_PRODUCT_RU_WB, LEXICON_PRODUCT_RU_WB_OZON
import os
from aiogram import Router, F
from WB_API.merge import stock_process, orders_process, union_sales, wb_order_graphics_by_sku, wb_ozon_order_graphics_by_sku, orders_process_3_month, wb_stock_dynamic, wb_expiration_date
from keyboards.inline_keyboards import keyboard_Ozon, keyboard_WB, keyboard_start, create_inline_kb, keyboard_WB_new, keyboard_Ozon_new, keyboard_Ozon_middle, keyboard_WB_middle
from WB_API.ozon_graphics import ozon_order_graphics, ozon_order_graphics_by_sku, ozon_order_graphics_3_month, ozon_stock_dynamic
from WB_API.ozon_stock_extract import ozon_stock_extract, ozon_stock_history
from WB_API.ozon_orders_extract import ozon_extract_orders
from WB_API.wb_stock_history import stock_history_extract
from WB_API.wb_unite_stock_orders import wb_stock_orders_unite
import json
from redis.asyncio import Redis

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

# Этот хэндлер будет срабатывать на апдейт Back
@router.callback_query(F.data=='Back')
async def process_callback_command_back(callback: CallbackQuery):
    await callback.message.edit_text(text="Выбери площадку", reply_markup=keyboard_start)

# Этот хэндлер будет срабатывать на апдейт Back_Middle_WB
@router.callback_query(F.data=='Back_Middle_WB')
async def process_callback_command_back_wb(callback: CallbackQuery):
    await callback.message.edit_text(text="Wildberries", reply_markup=keyboard_WB_new)

# Этот хэндлер будет срабатывать на апдейт Back_Middle_Ozon
@router.callback_query(F.data=='Back_Middle_Ozon')
async def process_callback_command_back_ozon(callback: CallbackQuery):
    await callback.message.edit_text(text="Ozon", reply_markup=keyboard_Ozon_new)

# Этот хэндлер будет срабатывать на апдейт SKU_WB
@router.callback_query(F.data=='SKU_WB')
async def process_callback_command_sku_wb(callback: CallbackQuery):
    kb = create_inline_kb(width=1, **LEXICON_PRODUCT_RU_WB)
    await callback.message.edit_text(text="Выбери SKU", reply_markup=kb)

# Этот хэндлер будет срабатывать на апдейт SKU_WB_OZON
@router.callback_query(F.data=='SKU_WB_OZON')
async def process_callback_command_sku_wb_ozon(callback: CallbackQuery):
    kb = create_inline_kb(width=1, **LEXICON_PRODUCT_RU_WB_OZON)
    await callback.message.edit_text(text="Выбери SKU", reply_markup=kb)

# Этот хэндлер будет срабатывать на апдейт SKU_OZON
@router.callback_query(F.data=='SKU_OZON')
async def process_callback_command_sku_ozon(callback: CallbackQuery):
    kb = create_inline_kb(width=1, **LEXICON_PRODUCT_RU)
    await callback.message.edit_text(text="Выбери SKU", reply_markup=kb)

# Этот хендлер срабатывает на команду /WB_Orders
@router.callback_query(F.data=='/WB_Orders')
async def process_orders_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(sticker='CAACAgIAAxkBAAEBoAZo1TavaUUQw3f9JWmuZmBRA-NG4AACsyEAAtApAAFJkghSY-eBYN82BA')
    img_path = orders_process()[1]
    img = FSInputFile(img_path)
    await callback.message.answer(text=LEXICON_RU['/orders'])
    await callback.message.reply_photo(photo=img)
    await callback.message.answer(text="Можно посмотреть детальнее по sku", reply_markup=keyboard_WB_middle)

# Этот хендлер срабатывает на команду /WB_Orders_3_Months
@router.callback_query(F.data=='/WB_Orders_3_Months')
async def process_orders_3_month_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(sticker='CAACAgIAAxkBAAEBoO5o17z5o4ICjxFyaKQj-9lrclXkzgAChB4AAsLNqEoDL_BkvnzjazYE')
    img_path = orders_process_3_month()
    img = FSInputFile(img_path)
    await callback.message.answer(text=LEXICON_RU['/orders'])
    await callback.message.reply_photo(photo=img)
    await callback.message.answer(text="Можно посмотреть детальнее по sku", reply_markup=keyboard_WB_middle)

# Этот хендлер срабатывает на команды по баркодам WB+Ozon
@router.callback_query(lambda x: x.data[:13].isdigit() and len(x.data)==14)
async def process_wb_ozon_orders_by_sku_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(sticker='CAACAgIAAxkBAAEBoAxo1T0CWmgAAd9LBBsSgBfSmVO2zb4AAlYfAAINfSFIvx1T2IVUIiM2BA')
    img_path = wb_ozon_order_graphics_by_sku(filter=str(callback.data[:13]))
    img = FSInputFile(img_path)
    await callback.message.answer(text=LEXICON_RU['/orders'])
    await callback.message.reply_photo(photo=img)
    await callback.message.answer(text="Wildberries+Ozon", reply_markup=keyboard_WB_new)

# Этот хендлер срабатывает на команды по баркодам
@router.callback_query(lambda x: x.data.isdigit() and len(x.data)==13)
async def process_wb_orders_by_sku_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(sticker='CAACAgIAAxkBAAEBoAxo1T0CWmgAAd9LBBsSgBfSmVO2zb4AAlYfAAINfSFIvx1T2IVUIiM2BA')
    img_path = wb_order_graphics_by_sku(filter=str(callback.data))
    img = FSInputFile(img_path)
    await callback.message.answer(text=LEXICON_RU['/orders'])
    await callback.message.reply_photo(photo=img)
    await callback.message.answer(text="Wildberries", reply_markup=keyboard_WB_new)

# Этот хендлер срабатывает на команду /WB_Stock
@router.callback_query(F.data=='/WB_Stock')
async def process_stock_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(
        sticker='CAACAgIAAxkBAAEBn_5o1TZqfGQ63BTKxBthggU1hNDiygACkRcAAmYJqEq49XihleTD1TYE')
    doc_path = stock_process()
    doc = FSInputFile(doc_path)
    await callback.message.answer(text=LEXICON_RU['/stock'])
    await callback.message.reply_document(document=doc)
    await callback.message.answer(text="Wildberries", reply_markup=keyboard_WB_new)

# Этот хендлер срабатывает на команду /WB_Expiration
@router.callback_query(F.data=='/WB_Expiration')
async def process_wb_expiration_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(
        sticker='CAACAgIAAxkBAAEBn_5o1TZqfGQ63BTKxBthggU1hNDiygACkRcAAmYJqEq49XihleTD1TYE')
    doc_path = wb_expiration_date()
    doc = FSInputFile(doc_path)
    await callback.message.answer(text=LEXICON_RU['/expiration'])
    await callback.message.reply_document(document=doc)
    await callback.message.answer(text="Wildberries", reply_markup=keyboard_WB_new)

# Этот хендлер срабатывает на команду /WH_Stock_history
@router.callback_query(F.data=='/WB_Stock_history')
async def process_wb_stock_history_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(
        sticker='CAACAgIAAxkBAAEBn_5o1TZqfGQ63BTKxBthggU1hNDiygACkRcAAmYJqEq49XihleTD1TYE')
    img_path = wb_stock_dynamic()
    img = FSInputFile(img_path)
    await callback.message.answer(text=LEXICON_RU['/stock_history'])
    await callback.message.reply_photo(photo=img)
    await callback.message.answer(text="Wildberries", reply_markup=keyboard_WB_new)

# Этот хендлер срабатывает на команду /Ozon_Stock_history
@router.callback_query(F.data=='/Ozon_Stock_history')
async def process_ozon_stock_history_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(
        sticker='CAACAgIAAxkBAAEBn_5o1TZqfGQ63BTKxBthggU1hNDiygACkRcAAmYJqEq49XihleTD1TYE')
    img_path = ozon_stock_dynamic()
    img = FSInputFile(img_path)
    await callback.message.answer(text=LEXICON_RU['/stock_history'])
    await callback.message.reply_photo(photo=img)
    await callback.message.answer(text="Ozon", reply_markup=keyboard_Ozon_new)

# Этот хендлер срабатывает на команду /Ozon_Orders
@router.callback_query(F.data=='/Ozon_Orders')
async def process_ozon_orders_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(
        sticker='CAACAgIAAxkBAAEBn_po1TZEEJPwpjvIiOWN3m85KUUiUwACXxwAApcAAahK5rAVXgI1dfI2BA')
    img_path = ozon_order_graphics()
    img = FSInputFile(img_path)
    await callback.message.answer(text=LEXICON_RU['/orders'])
    await callback.message.reply_photo(photo=img)
    await callback.message.answer(text="Можно посмотреть детальнее по sku", reply_markup=keyboard_Ozon_middle)

# Этот хендлер срабатывает на команду /Ozon_Orders_3_Months
@router.callback_query(F.data=='/Ozon_Orders_3_Months')
async def process_ozon_orders_3_month_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(
        sticker='CAACAgIAAxkBAAEBoOxo17xtpJVojv1H--s88ikl9W_8lQACNDMAAuM4eEq5VO2KVCH-FTYE')
    img_path = ozon_order_graphics_3_month()
    img = FSInputFile(img_path)
    await callback.message.answer(text=LEXICON_RU['/orders'])
    await callback.message.reply_photo(photo=img)
    await callback.message.answer(text="Можно посмотреть детальнее по sku", reply_markup=keyboard_Ozon_middle)

# Этот хендлер срабатывает на команды по ozon_sku
@router.callback_query(lambda x: x.data.isdigit() and (len(x.data)==10 or len(x.data)==9))
async def process_ozon_orders_by_sku_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(
        sticker='CAACAgIAAxkBAAEBn_ho1TYjmxJahNXbF1xN85lYxENySwACYR8AAsglqErRJ4xKhU8H1DYE')
    img_path = ozon_order_graphics_by_sku(filter=str(callback.data))
    img = FSInputFile(img_path)
    await callback.message.answer(text=LEXICON_RU['/orders'])
    await callback.message.reply_photo(photo=img)
    await callback.message.answer(text="Ozon", reply_markup=keyboard_Ozon_new)

# Этот хендлер срабатывает на команду /Ozon_Stock
@router.callback_query(F.data=='/Ozon_Stock')
async def process_ozon_stock_command(callback: CallbackQuery):
    await callback.answer(text=LEXICON_RU['/wait'], show_alert=True)
    await callback.message.reply_sticker(
        sticker='CAACAgIAAxkBAAEBnglo0l9kI8plUYwJt75T0DCM-7ySTQACSGoAAt7oeUnaJPE98T9j_jYE')
    doc_path = ozon_stock_extract()
    doc = FSInputFile(doc_path)
    await callback.message.answer(text=LEXICON_RU['/stock'])
    await callback.message.reply_document(document=doc)
    await callback.message.answer(text="Ozon", reply_markup=keyboard_Ozon_new)

# Этот хендлер срабатывает на команду /WhoIsOrta
@router.message(F.text=='/WhoIsOrta')
async def process_who_command(message: Message):
    img_path = os.path.join(os.path.dirname(__file__), 'who.png')
    img = FSInputFile(img_path)
    await message.reply_photo(photo=img)

# Этот хендлер срабатывает на команду /stat
@router.message(F.text == '/stat')
async def process_stat_command(message: Message, redis: Redis):
    keys = await redis.keys("user:*")
    if not keys:
        await message.answer("Нет данных о пользователях.")
        return

    text = "📊 Статистика:\n\n"
    for key in keys:
        user_json = await redis.get(key)
        if not user_json:
            continue
        user_data = json.loads(user_json)
        text += (
            f"👤 {user_data['username']}\n"
            f"Запросов: {user_data['requests_qty']}\n"
            f"Последний: {user_data['last_requests_date']}\n\n"
        )
    await message.answer(text)

# Этот хендлер срабатывает на команду /wb_update
@router.message(F.text == '/wb_update')
async def process_wb_update_command(message: Message):
    data = union_sales()
    await message.answer(text='Началось обновление продаж WB')

# Этот хендлер срабатывает на команду /wb_update_stock
@router.message(F.text == '/wb_update_stock')
async def process_wb_update_stock_command(message: Message):
    data = stock_history_extract()
    await message.answer(text='WB сток обновлён')

# Этот хендлер срабатывает на команду /ozon_update_stock
@router.message(F.text == '/ozon_update_stock')
async def process_ozon_update_stock_command(message: Message):
    data = ozon_stock_history()
    await message.answer(text='Ozon сток обновлён')

# Этот хендлер срабатывает на команду /wb_update_stock_sales
@router.message(F.text == '/wb_update_stock_sales')
async def process_wb_update_stock_sales_command(message: Message):
    data = wb_stock_orders_unite()
    await message.answer(text='WB сток и продажи объединены')

# Этот хендлер срабатывает на команду /ozon_update
@router.message(F.text == '/ozon_update')
async def process_ozon_update_command(message: Message):
    data = ozon_extract_orders()
    await message.answer(text='Началось обновление продаж Ozon')

# Этот хендлер срабатывает на остальные сообщения
@router.message()
async def process_other_message(message: Message):
    await message.answer(text=LEXICON_RU['no_echo'])