import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Создаем объекты инлайн-кнопок
button_1 = InlineKeyboardButton(text="Wildberries", callback_data="Wildberries")
button_2 = InlineKeyboardButton(text="Ozon", callback_data="Ozon")

# Создаем объект клавиатуры
keyboard_start = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]])

button_1_1 = InlineKeyboardButton(text="WB_Orders", callback_data="/WB_Orders")
button_1_2 = InlineKeyboardButton(text="WB_Stock", callback_data="/WB_Stock")
button_2_1 = InlineKeyboardButton(text="Ozon_Orders", callback_data="/Ozon_Orders")
button_2_2 = InlineKeyboardButton(text="Ozon_Stock", callback_data="/Ozon_Stock")
button_back = InlineKeyboardButton(text="Back", callback_data="Back")

keyboard_WB = InlineKeyboardMarkup(inline_keyboard=[[button_1_1, button_1_2, button_back]])
keyboard_Ozon = InlineKeyboardMarkup(inline_keyboard=[[button_2_1, button_2_2, button_back]])

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
