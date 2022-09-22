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

RETRY_TIME: int = 60 * 10
CURRENT_TIME = int(time.time())
WEEK: int = 7 * 24 * 60 * 60

HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}
ENDPOINT = "https://practicum.yandex.ru/api/user_api/hom_ework_statuses/"

request_params = {
    "url": ENDPOINT,
    "headers": HEADERS,
    "params": {"from_date": CURRENT_TIME - WEEK}
}
HOMEWORK_VERDICTS = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания."
}


def send_message(bot, message):
    """Отправка сообщения в чат."""
    logger.info("Начинаем отправлять сообщение пользователю.")
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
    except Exception as error:
        raise KeyError(
            f"Ошибка '{error}', при отправке сообщения '{message}'."
        )
    else:
        logger.info(f"Удачная отправка сообщения '{message}' пользователю.")


def get_api_answer(request_params):
    """Получаем ответ от API Практикум.Домашка."""
    logger.info("Получаем ответ от API.")
    try:
        homeworks = requests.get(**request_params)
    except Exception as error:
        logger.error(f"Сбой '{error}' при запросе к эндпоинту.")
        raise KeyError(f"Сбой '{error}' при запросе к эндпоинту.")
    status_code = homeworks.status_code
    if status_code != HTTPStatus.OK:
        raise KeyError(
            f"Status_code при запросе с параметрами {request_params}"
            f" -> {status_code} вместо 200"
        )
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
    if not isinstance(response, dict):
        logger.error("Ответ API это не словарь!")
        raise TypeError("Ответ API это не словарь!")
    if "homeworks" not in response:
        logger.error("В ответе от API нет домашек.")
        raise KeyError("В ответе от API нет домашек.")
    list_hws = response["homeworks"]
    if not isinstance(list_hws, list):
        logger.error("В ответе API нет списка работ.")
        raise TypeError("В ответе API нет списка работ.")
    return list_hws


def parse_status(homework):
    """Извлекаем информацию о конкретной домашней работе."""
    logger.info("Извлекаем информацию о конкретной домашней работе.")
    if "homework_name" not in homework:
        logger.error("В homework нет ключа 'homework_name'")
        raise KeyError("В homework нет ключа 'homework_name'")
    if not homework["homework_name"]:
        logger.error("В homework нет значения по ключу 'homework_name'")
        raise KeyError("В homework нет значения по ключу 'homework_name'")
    if "status" not in homework:
        logger.error("В homework нет ключа 'status'")
        raise KeyError("В homework нет ключа 'status'")
    if not homework["status"]:
        logger.error("В homework нет значения по ключу 'status'")
        raise KeyError("В homework нет значения по ключу 'status'")
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")
    try:
        verdict = HOMEWORK_VERDICTS[homework_status]
    except Exception:
        logger.error(
            f"Статуса {homework_status} нет в 'HOMEWORK_VERDICTS'."
        )
        raise KeyError(
            f"Статуса {homework_status} нет в 'HOMEWORK_VERDICTS'."
        )
    logger.info(
        f"Изменился статус проверки работы '{homework_name}'. {verdict}"
    )
    return f"Изменился статус проверки работы '{homework_name}'. {verdict}"


def check_tokens():
    """Проверяем доступность переменных окружения."""
    logger.info("Проверяем доступность переменных окружения")
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical("Переменные окружения недоступны!")
        raise KeyError("Переменные окружения недоступны!")
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    statuses = []
    while True:
        try:
            response = get_api_answer(request_params)
            list_hws = check_response(response)
            try:
                (list_hws[0])
            except Exception:
                logger.critical("Нет работ на проверке.")
                raise KeyError("Нет работ на проверке.")
            hw = list_hws[0]
            message = parse_status(hw)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.critical(f"Ошибка -> {message}")
        finally:
            if message in statuses:
                logger.debug("Новых статусов нет")
            else:
                statuses.append(message)
                send_message(bot, message)
            logger.info("-.-.-.-.-Окончание итерации-.-.-.-.-")
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(__file__ + ".log", encoding="UTF-8")
        ],
        format=u"%(name)s || %(funcName)s || [LINE:%(lineno)d]#"
               u"%(levelname)s || [%(asctime)s] || %(message)s"
    )
    logger = logging.getLogger(__name__)
    main()
