import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_TIME = 600
CURRENT_TIME = int(time.time())
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    filename=u"hwr.log",
    format=u"%(name)s[LINE:%(lineno)d]#"
           u"%(levelname)-8s [%(asctime)s]  %(message)s"
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream="sys.stdout")
logger.addHandler(handler)


def send_message(bot, message):
    """Отправка сообщения в чат."""
    try:
        logger.info("Начинаем отправлять сообщение пользователю.")
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logger.info(f"Удачная отправка сообщения '{message}' пользователю.")
    except Exception as error:
        logger.error(
            f"Ошибка '{error}', при отправке сообщения '{message}'."
        )
        raise KeyError(
            f"Ошибка '{error}', при отправке сообщения '{message}'."
        )


def get_api_answer(current_timestamp):
    """Получаем ответ от API Практикум.Домашка."""
    timestamp = current_timestamp or CURRENT_TIME
    params = {"from_date": timestamp}
    try:
        homeworks = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except Exception as error:
        logger.error(f"Сбой '{error}' при запросе к эндпоинту.")
        raise KeyError(f"Сбой '{error}' при запросе к эндпоинту.")
    status_code = homeworks.status_code
    if status_code != HTTPStatus.OK:
        logger.error(f"Status_code сервера API {status_code}, а не 200.")
        raise KeyError(f"Status_code сервера API {status_code}, а не 200.")
    try:
        response = homeworks.json()
    except Exception as error:
        logger.error(f"Сбой '{error}' при переводе в json.")
        raise KeyError(f"Сбой '{error}' при переводе в json.")
    return response


def check_response(response):
    """Проверяем корректность ответа от API."""
    logger.info("Проверяем корректность ответа от API.")
    if not response:
        logger.error("От API получен пустой словарь.")
        raise KeyError("От API получен пустой словарь.")
    if type(response) is not dict:
        logger.error("Ответ API это не словарь!")
        raise TypeError("Ответ API это не словарь!")
    if "homeworks" not in response:
        logger.error("В ответе от API нет домашек.")
        raise KeyError("В ответе от API нет домашек.")
    list_hws = response["homeworks"]
    if type(list_hws) is not list:
        logger.error("В ответе API нет списка работ.")
        raise TypeError("В ответе API нет списка работ.")
    return list_hws


def parse_status(homework):
    """Извлекаем информацию о конкретной домашней работе."""
    logger.info("Извлекаем информацию о конкретной домашней работе.")
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except Exception:
        logger.error(
            f"Статуса {homework_status} нет в 'HOMEWORK_STATUSES'."
        )
        raise KeyError(
            f"Статуса {homework_status} нет в 'HOMEWORK_STATUSES'."
        )
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяем доступность переменных окружения."""
    logger.info("Проверяем доступность переменных окружения")
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical("Переменные окружения недоступны!")
        raise KeyError("Переменные окружения недоступны!")
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    statuses = []
    while True:
        try:
            response = get_api_answer(current_timestamp)
            list_hws = check_response(response)
            try:
                (list_hws[0])
            except Exception:
                logger.critical("Нет работ на проверке.")
                raise KeyError("Нет работ на проверке.")
            hw = list_hws[0]
            message = parse_status(hw)
            current_timestamp = response.get("current_date")
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.critical(f"Ошибка {message}")
        finally:
            if message in statuses:
                logger.debug("Новых статусов нет")
            else:
                statuses.append(message)
                send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
