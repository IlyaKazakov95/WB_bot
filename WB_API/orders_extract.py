import requests
import datetime as datetime
import json
from environs import Env

def orders_extract():
    env = Env()
    env.read_env()
    url = 'https://statistics-api.wildberries.ru/api/v1/supplier/orders'
    target_date = datetime.date.today() + datetime.timedelta(days = -90)
    response = requests.get(url, headers={"Authorization": env("HeaderApiToken")}, params={'flag':0,'dateFrom': target_date})
    response = response.json()
    with open('orders.json', 'w', encoding="utf-8") as f:
        f.write(json.dumps(response, ensure_ascii=False, indent=4))