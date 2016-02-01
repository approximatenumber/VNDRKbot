# VNDRKbot Telegram Bot On Python

Бот для оповещения своих подписчиков о новых событиях на сайте vandrouki.ru. [Echobot.py](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/legacy/echobot.py) используется в качестве каркаса для бота.

## Запуск
`pip install -r requirements.txt` 
`./bot.py` 

## Что нужно исправить/добавить?
1. Убрать параллельное выполнение функций. Вместо этого выполнять их последовательно, используя таймаут.
2. Добавить более гибкую обработку ошибок. Пока что есть несколько try/except, которые просто «рубят с плеча».
3. Убрать глобальные переменные.
