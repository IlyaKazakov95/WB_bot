import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Создаем объекты инлайн-кнопок
button_1 = InlineKeyboardButton(text="Wildberries", callback_data="Wildberries")
button_2 = InlineKeyboardButton(text="Ozon", callback_data="Ozon")

# Создаем объект клавиатуры
keyboard_start = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]])

button_1_1 = InlineKeyboardButton(text="ВБ Заказы", callback_data="/WB_Orders")
button_1_2 = InlineKeyboardButton(text="ВБ Остатки", callback_data="/WB_Stock")
button_2_1 = InlineKeyboardButton(text="Озон Заказы", callback_data="/Ozon_Orders")
button_2_2 = InlineKeyboardButton(text="Озон Остатки", callback_data="/Ozon_Stock")
button_back = InlineKeyboardButton(text="Назад", callback_data="Back")
button_sku_wb = InlineKeyboardButton(text="Продолжить по скю", callback_data="SKU_WB")
button_sku_ozon = InlineKeyboardButton(text="Продолжить по скю", callback_data="SKU_OZON")
button_back_middle_wb = InlineKeyboardButton(text="Назад", callback_data="Back_Middle_WB")
button_back_middle_ozon = InlineKeyboardButton(text="Назад", callback_data="Back_Middle_Ozon")
button_sku_wb_ozon = InlineKeyboardButton(text="ВБ+Озон по скю", callback_data="SKU_WB_OZON")
button_ozon_3month = InlineKeyboardButton(text="Озон Заказы 3 месяца", callback_data="/Ozon_Orders_3_Months")
button_wb_3month = InlineKeyboardButton(text="ВБ Заказы 3 месяца", callback_data="/WB_Orders_3_Months")
button_wb_stock = InlineKeyboardButton(text="ВБ Динамика Стока", callback_data="/WB_Stock_history")
button_wb_expiration = InlineKeyboardButton(text="ВБ ОСГ", callback_data="/WB_Expiration")

keyboard_WB = InlineKeyboardMarkup(inline_keyboard=[[button_1_1, button_1_2], [button_wb_3month, button_back], [button_wb_stock, button_wb_expiration]])
keyboard_Ozon = InlineKeyboardMarkup(inline_keyboard=[[button_2_1, button_2_2],[button_ozon_3month, button_back]])

keyboard_WB_new = InlineKeyboardMarkup(inline_keyboard=[[button_1_1, button_1_2], [button_sku_wb, button_sku_wb_ozon], [button_wb_stock, button_wb_expiration], [button_wb_3month, button_back]])
keyboard_Ozon_new = InlineKeyboardMarkup(inline_keyboard=[[button_2_1, button_2_2], [button_sku_ozon, button_sku_wb_ozon], [button_ozon_3month, button_back]])

keyboard_WB_middle = InlineKeyboardMarkup(inline_keyboard=[[button_sku_wb, button_back_middle_wb]])
keyboard_Ozon_middle = InlineKeyboardMarkup(inline_keyboard=[[button_sku_ozon, button_back_middle_ozon]])

# Функция для формирования инлайн клавиатуры на лету
def create_inline_kb(
        width: int,
        *args: str,
        **kwargs: str
) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kp_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []
    #заполняем список кнопками из args и kwargs
    if args:
        for arg in args:
            buttons.append(InlineKeyboardButton(text=arg, callback_data=arg))
    if kwargs:
        for key, value in kwargs.items():
            buttons.append(InlineKeyboardButton(text=value, callback_data=key))
    # распаковываем список с кнопками
    kp_builder.row(*buttons, width=width)
    kp_builder.row(InlineKeyboardButton(text='Назад', callback_data="Back"))
    # возвращаем объект инлайн-клавиатуры
    return kp_builder.as_markup()
