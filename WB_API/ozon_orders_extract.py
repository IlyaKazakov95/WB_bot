import requests
from environs import Env
import json
import time
import pandas as pd
import datetime as datetime

def ozon_extract_orders():
    env = Env()
    env.read_env()
    url = 'https://api-seller.ozon.ru/v2/posting/fbo/list'
    since = datetime.datetime.today()- datetime.timedelta(days = 180)
    to = datetime.datetime.today()
    since_str = str(since.isoformat() + "Z")
    to_str = str(to.isoformat() + "Z")
    print(since, to)
    offset = 0
    json_dict = {}
    flag = 1
    counter = 0
    while True:
        while offset <= 20000:
            response = requests.post(url, headers={'Client-Id': env('Client_Id'), 'Api-Key': env('API_Key'),
                                                   'Content-Type': 'application/json'},
                                     json={'dir': 'ASC', 'offset': offset, 'limit': 1000, 'filter': {'since': since_str, 'to': to_str},
                                           'with': {'analytics_data': True, 'financial_data': True}})
            response = response.json()
            try:
                if len(response['result']) == 0:
                    break
            except Exception:
                print("Error")
                break
            json_dict[counter * 100000 + offset // 1000] = response # так как 2 цикла делаем уникальный ключ за счет counter и offset, возможно counter нужно сделать еще большим
            print(len(response), offset)
            offset += 1000
            time.sleep(1)
        counter += 1
        to = since - datetime.timedelta(days = 1)
        since = to - datetime.timedelta(days = 180)
        if to < datetime.datetime(2024, 1, 1):
            break
        if since < datetime.datetime(2024, 1, 1):
            since = datetime.datetime(2024, 1, 1)
        since_str = str(since.isoformat() + "Z")
        to_str = str(to.isoformat() + "Z")
        offset = 0
    merged = list(json_dict.values())
    merged_results = []
    for m in merged:
        merged_results.extend(m['result'])
    df = pd.DataFrame(merged_results)
    # "разворачиваем" список продуктов на строки
    df_exploded = df.assign(
        products=df["products"].apply(lambda x: x if isinstance(x, list) else [])).explode("products", ignore_index=True)
    df_products = pd.json_normalize(df_exploded["products"].dropna())
    # соединяем обратно
    df_orders = pd.concat([df_exploded.drop(columns=["products"]), df_products], axis=1)
    df_orders_final = df_orders.assign(
                          warehouse_id=df_orders["analytics_data"].apply(lambda x: x['warehouse_id'] if isinstance(x, dict) else None),
                          warehouse_name=df_orders["analytics_data"].apply(lambda x: x['warehouse_name'] if isinstance(x, dict) else None),
                          cluster_from=df_orders["financial_data"].apply(lambda x: x['cluster_from'] if isinstance(x, dict) else None),
                          cluster_to=df_orders["financial_data"].apply(lambda x: x['cluster_to'] if isinstance(x, dict) else None))[["order_number",
                                                                                             "posting_number",
                                                                                             "status",
                                                                                             "created_at",
                                                                                             "sku",
                                                                                             "name",
                                                                                             "quantity",
                                                                                             "warehouse_id",
                                                                                             "warehouse_name",
                                                                                             "cluster_from",
                                                                                             "cluster_to"]]
    df_orders_final.to_excel("ozon_orders.xlsx", sheet_name="Sheet1", index=False)