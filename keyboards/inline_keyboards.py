import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создаем объекты инлайн-кнопок
button_1 = InlineKeyboardButton(text="Wildberries", callback_data="Wildberries")
button_2 = InlineKeyboardButton(text="Ozon", callback_data="Ozon")

# Создаем объект клавиатуры
keyboard_start = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]])

button_1_1 = InlineKeyboardButton(text="WB_Orders", callback_data="WB_Orders")
button_1_2 = InlineKeyboardButton(text="WB_Stock", callback_data="WB_Stock")
button_2_1 = InlineKeyboardButton(text="Ozon_Orders", callback_data="Ozon_Orders")
button_2_2 = InlineKeyboardButton(text="Ozon_Stock", callback_data="Ozon_Stock")
button_back = InlineKeyboardButton(text="Назад", callback_data="Back")

keyboard_WB = InlineKeyboardMarkup(inline_keyboard=[[button_1_1, button_1_2, button_back]])
keyboard_Ozon = InlineKeyboardMarkup(inline_keyboard=[[button_1_1, button_1_2, button_back]])
