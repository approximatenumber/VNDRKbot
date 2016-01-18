# VNDRKbot Telegram Bot On Python

Бот для оповещения своих подписчиков о новых событиях на сайте vandrouki.ru.

За основу мною был взят пример [echobot.py](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/legacy/echobot.py).

## Что нужно исправить/добавить?
1. Убрать параллельное выполнение функций. Вместо этого выполнять их последовательно, используя таймаут.
2. Добавить более гибкую обработку ошибок. Пока что есть несколько try/except, которые работают «рубят с плеча».
3. 

## Требования?
`python3`
<br>
`python-telegram-bot`
<br>
`beautifulsoup4`
