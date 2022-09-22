import os
import time

from dotenv import load_dotenv

load_dotenv()
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")

CURRENT_TIME = int(time.time())
WEEK: int = 7 * 24 * 60 * 60

HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
params = {"from_date": CURRENT_TIME - WEEK}

request_params = {
    "url": ENDPOINT,
    "headers": HEADERS,
    "params": params
}

print(**request_params)
