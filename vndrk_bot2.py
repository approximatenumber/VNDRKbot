#!/usr/bin/env python

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot, TelegramError
import logging
import sys
import os
from tinydb import TinyDB, Query
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
chats = 'chats.json'
news_file = 'news.db'
URL = "http://vandrouki.ru"

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

    def check_update(self, downloaded_news, stored_news):
        if downloaded_news != stored_news:
            return True
        else:
            return False


def main(**args):

    def start(bot, update):
        message = update.message
        chat_id = message.chat.id
        if not chat_db.contains(chats_query.chat_id == chat_id):
            chat_db.insert({'chat_id': chat_id})
            text = 'Вы подписаны на рассылку vandrouki.ru!'
            bot.sendMessage(chat_id=chat_id, text=text)
            logging.warning('%s added' % chat_id)

    def stop(bot, update):
        message = update.message
        chat_id = message.chat.id
        if chat_db.contains(chats_query.chat_id == chat_id) is True:
            chat_db.remove(chats_query.chat_id == chat_id)
            text = 'Вы отписались от рассылки vandrouki.ru!'
            bot.sendMessage(chat_id=chat_id, text=text)
            logging.warning('%s removed' % chat_id)

    def send_msg(chat_id, text):
        try:
            Bot(token=TOKEN).sendMessage(chat_id, text)
        except TelegramError as err:
            if err.message == "Unauthorized":
                chat_db.remove(chats_query.chat_id == chat_id)
                logging.warning('%s blocked us, so removed' % chat_id)
            else:
                logging.error('Error for %s: %s' % (chat_id, err))


    chat_db = TinyDB(chats)
    chats_query = Query()

    
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    # dp.add_error_handler(error)
    updater.start_polling()

    news = News(news_file)
    stored_news_link = news.read('link')
    downloaded_news_link, downloaded_news_text = news.download()
    print('stored: %s, down: %s' % (stored_news_link, downloaded_news_link))
    if news.check_update(downloaded_news_link, stored_news_link) is True:
        news.store('link', downloaded_news_link)
        news.store('text', downloaded_news_text)
    else:
        print('the same')


if __name__ == '__main__':
    main()
