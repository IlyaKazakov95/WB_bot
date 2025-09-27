import pandas as pd
from pathlib import Path

LEXICON_RU: dict[str, str] = {
    '/start': 'Привет!\n\nЯ бот-помощник для работы с Wildberries и Ozon\n'
              'Пока в мой функционал входит отправка текущих стоков в днях покрытия и график продаж за 3 месяца\n'
              'Но постепенно моя функциональность будет увеличиваться\n'
              'Для того, чтобы понять, как со мной работать, напиши /help',
    '/help': 'Выбери площадку Wildberries или Ozon, c которой хочешь поработать\n'
                'Далее я могу прислать тебе аналитику по стокам и продажам при выборе соответсвующих разделов\n'
             'Отчеты могут формироваться до 1 минуты, в это время не нажимай других кнопок\n',
    'no_echo': 'Я тебя не понимаю, посмотри инструкцию /help',
    '/stock': 'Отправляю тебе текущие стоки в абсолютах и днях покрытия',
    '/orders': 'Отправляю тебе график с текущими продажами',
    '/wait': 'Формирую отчёт, подождите... Ожидание может быть до 1 мин'
}

LEXICON_COMMANDS_RU: dict[str, str] = {
    '/start': 'Перезапуск бота',
    '/help': 'Инструкция по работе бота'
    #,'/orders': 'Выгрузка заказов за 3 месяца',
    #'/stock': 'Выгрузка текущего стока'
}


current_file = Path(__file__).resolve()
file = current_file.parent / 'Mapping.xlsx'
df = pd.read_excel(file)
df3 = df[["Ozon_SKU", "Наименование"]].reset_index()
df3 = df3.sort_values(by = ["Наименование"], ascending = False)
LEXICON_PRODUCT_RU: dict[str, str] = {}
for index, row in df3.iterrows():
    LEXICON_PRODUCT_RU[str(row['Ozon_SKU'])] = row['Наименование']

df2 = df[["barcode", "Наименование"]].reset_index()
df2 = df2.sort_values(by = ["Наименование"], ascending = False)
LEXICON_PRODUCT_RU_WB: dict[str, str] = {}
for index, row in df2.iterrows():
    LEXICON_PRODUCT_RU_WB[str(row['barcode'])] = row['Наименование']

df4 = df[["barcode", "Наименование"]].reset_index()
df4 = df4.sort_values(by = ["Наименование"], ascending = False)
LEXICON_PRODUCT_RU_WB_OZON: dict[str, str] = {}
for index, row in df4.iterrows():
    LEXICON_PRODUCT_RU_WB_OZON[str(row["barcode"])+'_'] = row['Наименование']

