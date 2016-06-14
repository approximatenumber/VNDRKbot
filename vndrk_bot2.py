#!/usr/bin/env python

from telegram import Bot, TelegramError
from telegram.ext import Updater, CommandHandler
from time import sleep
import logging
import sys
import pickledb as pkl
from bs4 import BeautifulSoup
from urllib.request import urlopen

try:
    sys.path.append('.private')
    from config import TOKEN       # importing secret TOKEN
except ImportError:
    print("TOKEN from .private/config.py needed!")
    raise SystemExit

log_file = "bot.log"
news_file = 'news.db'
chat_file = 'chats.db'
URL = "http://vandrouki.ru"
TIMEOUT = 180

logging.basicConfig(level=logging.WARNING, filename=log_file, format='%(asctime)s:%(levelname)s - %(message)s')
logging.FileHandler(log_file, mode='w')
logger = logging.getLogger(__name__)


class News():
    def __init__(self, news_file):
        self.news_db = pkl.load(news_file, False)
        if not self.news_db.get('link'):
            self.news_db.set('link', 'empty')
        if not self.news_db.get('text'):
            self.news_db.set('text', 'empty')

    def read(self, key):
        value = self.news_db.get(key)
        return value

    def store(self, key, value):
        self.news_db.set(key, value)
        self.news_db.dump()

    def download(self):
        soup = BeautifulSoup(urlopen(URL), "html.parser")
        link = soup.findAll('a', {'rel': 'bookmark'})[0].get("href")
        text = soup.findAll('a', {'rel': 'bookmark'})[0].getText()
        return link, text

    def check_update(self, old, new):
        if old != new:
            return True
        else:
            return False


class Chats():
    def __init__(self, chat_file):
        self.chat_db = pkl.load(chat_file, False)
        try:
            num = self.chat_db.llen('chats')
            logging.warning('chats in DB: %s' % num)
        except KeyError:
            self.chat_db.lcreate('chats')
            logging.warning('chat DB created')

    def add(self, chat_id):
        self.chat_db.ladd('chats', chat_id)
        self.chat_db.dump()

    def remove(self, chat_id):
        for num in range(self.chat_db.llen('chats')):
            if chat_id == self.chat_db.lget('chats', num):
                self.chat_db.lpop('chats', num)
                self.chat_db.dump()

    def contains(self, chat_id):
        for num in range(self.chat_db.llen('chats')):
            if chat_id == self.chat_db.lget('chats', num):
                return True
            return False

    def getall(self):
        return self.chat_db.lgetall('chats')


def main(**args):

    def start(bot, update):
        message = update.message
        chat_id = message.chat.id
        if not chats.contains(chat_id):
            chats.add(chat_id)
            text = 'Вы подписаны на рассылку vandrouki.ru!'
            bot.sendMessage(chat_id=chat_id, text=text)
            logging.warning('%s added' % chat_id)
        else:
            text = 'Вы уже подписаны!'
            bot.sendMessage(chat_id=chat_id, text=text)

    def stop(bot, update):
        message = update.message
        chat_id = message.chat.id
        if chats.contains(chat_id):
            chats.remove(chat_id)
            text = 'Вы отписались от рассылки vandrouki.ru!'
            bot.sendMessage(chat_id=chat_id, text=text)
            logging.warning('%s removed' % chat_id)
        else:
            text = 'Вы уже отписались!'
            bot.sendMessage(chat_id=chat_id, text=text)

    def send_msg(chat_id, text):
        try:
            Bot(token=TOKEN).sendMessage(chat_id, text)
        except TelegramError as err:
            if err.message == "Unauthorized":
                chats.remove(chat_id)
                logging.warning('%s blocked us, so removed' % chat_id)
            else:
                logging.error('Telegram error: chat_id %s, %s' % (chat_id, err))

    def error(bot, update, error):
        logging.warning('Update "%s" caused error "%s"' % (update, error))
        sleep(10)

    news = News(news_file)
    chats = Chats(chat_file)

    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_error_handler(error)
    updater.start_polling()

    while True:
        try:
            stored_link = news.read('link')
            downloaded_link, downloaded_text = news.download()
            if news.check_update(stored_link, downloaded_link) is True:
                news.store('link', downloaded_link)
                news.store('text', downloaded_text)
                for chat_id in chats.getall():
                    message = news.read('text') + '\n' + news.read('link')
                    send_msg(chat_id, message)
        except Exception as err:
            logging.error('Error while processing: %s' % err)
        sleep(TIMEOUT)

if __name__ == '__main__':
    main()
