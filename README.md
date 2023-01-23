# Телеграм-бот

## Описание

### Телеграм-бот/ассистент.
Обращается к API сервиса Практикум.Домашка для получения статуса проверки домашних работ.

Принцип работы бота:
- Раз в 10 минут опрашивает API сервиса Практикум.Домашка ([документация и примеры запросов](https://code.s3.yandex.net/backend-developer/learning-materials/delugov/%D0%9F%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D0%BA%D1%83%D0%BC.%D0%94%D0%BE%D0%BC%D0%B0%D1%88%D0%BA%D0%B0%20%D0%A8%D0%BF%D0%B0%D1%80%D0%B3%D0%B0%D0%BB%D0%BA%D0%B0.pdf)) и проверяет статус отправленной на ревью домашней работы.
- При обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram
- Если работа проверена вы получите сообщение о статусе вашего код ревью.
- Логирует свою работу и сообщает о важных проблемах сообщением в Telegram.

#### Технологии

- [Python 3.7+](https://www.python.org/)
- [python-telegram-bot](https://docs.python-telegram-bot.org/en/stable/)

#### Запуск проекта (Dev-режим)

- Склонируйте репозиторий:  
``` git clone https://github.com/owlproh/homework_bot.git ``` 

- Скопировать .env.example и назвать его .env:  
``` cp .env.example .env ```

- Заполнить переменные окружения в .env:  
``` PRACTICUM_TOKEN = токен к API Практикум.Домашка ```  
``` TELEGRAM_TOKEN = токен Вашего Telegtam бота ```  
``` TELEGRAM_CHAT_ID = Ваш Telegram ID ```

- Установите и активируйте виртуальное окружение:  
``` py -m venv venv ```  
``` source venv/Scripts/activate ``` 

- Установите зависимости из файла requirements.txt:   
``` pip install -r requirements.txt ```

#### Автор
[Прохоренко Святослав](http://github.com/owlproh)
