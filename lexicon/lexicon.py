import pandas as pd
from pathlib import Path

LEXICON_RU: dict[str, str] = {
    '/start': 'Привет!\n\nЯ бот-помощник для работы с Wildberries и Ozon\n'
              'Пока в мой функционал входит отправка текущих стоков в днях покрытия и график продаж за 3 месяца\n'
              'Но постепенно моя функциональность будет увеличиваться\n'
              'Для того, чтобы понять, как со мной работать, напиши /help',
    '/help': 'При отправке команды /stock я пришлю текущие стоки в днях покрытия\n'
                'При отправке команды /orders я пришлю график с продажами за 3 месяца',
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
df = df[["barcode", "Наименование"]].reset_index()
LEXICON_PRODUCT_RU: dict[str, str] = {}
for index, row in df.iterrows():
    LEXICON_PRODUCT_RU[str(row['barcode'])] = row['Наименование']
print(LEXICON_PRODUCT_RU)