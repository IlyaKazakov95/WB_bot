import requests
import datetime as dt
import pandas as pd
from pathlib import Path
from openpyxl import load_workbook
from environs import Env
import time

url = 'https://seller-analytics-api.wildberries.ru/api/v1/paid_storage'

env = Env()
env.read_env()


def safe_request(url, headers, params=None):
    while True:
        response = requests.get(url, headers=headers, params=params, verify=True)
        if response.status_code == 429:
            retry_after = int(response.headers.get("X-Ratelimit-Retry", 5))
            print(f"429 Too Many Requests, жду {retry_after} сек...")
            time.sleep(retry_after)
            continue
        return response


def append_to_excel(df, path, sheet_name="Sheet1"):
    book = load_workbook(path)
    startrow = book[sheet_name].max_row
    with pd.ExcelWriter(path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        df.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False, header=False)


def stock_history_extract():
    dateTo = dt.date.today()
    dateFrom = dateTo - dt.timedelta(days=6)
    file_name = "wb_stock_history.xlsx"
    path = Path(__file__).parent / file_name

    df_stock = pd.read_excel(path)
    df_stock["date"] = pd.to_datetime(df_stock["date"]).dt.date
    date_filter = max(df_stock['date'])

    if dateFrom <= date_filter:
        dateFrom = date_filter + dt.timedelta(days=1)
    if dateTo <= date_filter:
        return path

    while True:
        # запрос task_id через safe_request
        response = safe_request(url, headers={"Authorization": env('HeaderApiToken')},
                                params={"dateFrom": dateFrom, "dateTo": dateTo})
        task_id = response.json()['data']['taskId']
        print("task_id:", task_id)

        # ждём формирования отчёта
        time.sleep(60)

        # запрос отчёта через safe_request
        getting_report = f'https://seller-analytics-api.wildberries.ru/api/v1/acceptance_report/tasks/{task_id}/download'
        report_response = safe_request(getting_report, headers={"Authorization": env('HeaderApiToken')})
        report_json = report_response.json()

        if not report_json:
            break

        # сразу записываем в Excel
        cols_needed = ["date", "warehouse", "giId", "barcode", "barcodesCount"]
        df = pd.DataFrame(report_json)[cols_needed]
        append_to_excel(df, path)

        # сдвигаем даты для следующей итерации
        dateTo = dateFrom - dt.timedelta(days=1)
        dateFrom = dateTo - dt.timedelta(days=6)

        if dateFrom <= date_filter:
            break

    return path