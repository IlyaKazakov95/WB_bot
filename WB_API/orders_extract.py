import requests
import datetime as datetime
import json
from environs import Env
from pathlib import Path

def orders_extract():
    env = Env()
    env.read_env()
    url = 'https://statistics-api.wildberries.ru/api/v1/supplier/orders'
    target_date = datetime.date.today() + datetime.timedelta(days = -180) # проверил что максимальный горизонт хранения 180 дней, хотя заявлено вообще 90
    response = requests.get(url, headers={"Authorization": env("HeaderApiToken")}, params={'flag':0,'dateFrom': target_date})
    response = response.json()
    json_path = Path(__file__).parent / "orders.json"
    with open(json_path, 'w', encoding="utf-8") as f:
        f.write(json.dumps(response, ensure_ascii=False, indent=4))
    return response
