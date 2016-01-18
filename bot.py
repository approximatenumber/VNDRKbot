#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Сodes of functions addSubscriber() and delSubscriber():
# 0 - well done
# 1 - something goes wrong
# 3 - no such user
# 4 - user is already in database

import logging
import telegram
from time import sleep
import re, os

import threading
from bs4 import BeautifulSoup
try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen # python 3.4.3
from urllib.error import URLError

user_db = "subscribers"
news = "last_news"
TIMEOUT = 30
URL = "http://vandrouki.ru"
token = ""

def main():

  def notificateUser():
    if getLastNews(1) == 0:
        with open(user_db,'r') as file:
            for subscriber in file.read().splitlines():
                bot.sendMessage(chat_id=subscriber,
                        text=open(news, 'r').read())
                logging.info('subscriber %s is notified' % subscriber)
                
  logging.basicConfig(
      filename='bot.log',
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  logging.info('Starting bot...')

  for file in news, user_db:
      if not os.path.exists(file):
          open(file, 'w').close()
          logging.info('news and user_db created')

  bot = telegram.Bot(token)
  try:
      update_id = bot.getUpdates()[0].update_id
  except IndexError:
      update_id = None

  latest_handling_ts = time.time()                                              # start our TIMEOUT
  while True:
      now = time.time()
      if now - latest_handling_ts > TIMEOUT:                                    # check if TIMEOUT is over,
          notificateUser()                                                      # then notificate users from our database
          latest_handling_ts = time.time()                                      # update start of TIMEOUT
      try:
          update_id = echo(bot, update_id)
      except telegram.TelegramError as e:
          # These are network problems with Telegram.
          if e.message in ("Bad Gateway", "Timed out"):
              sleep(1)
          elif e.message == "Unauthorized":
              # The user has removed or blocked the bot.
              update_id += 1
          else:
              raise e
      except URLError as e:
          # These are network problems on our end.
          sleep(1)

def addSubscriber(chat_id):
  try:
    if os.path.exists(user_db):
      with open(user_db,'r') as file:
        if str(chat_id) in file.read().splitlines():
          logging.info('subscriber %s already in database' % chat_id)
          return 4
          pass
        else:
          with open(user_db,'a') as file:
            file.write(str(chat_id) + '\n')
          logging.info('added %s' % chat_id)
          return 0
    else:                                       # db does not exist
      with open(user_db,'w') as file:
        file.write(str(chat_id) + '\n')
      logging.info('DB created! added %s' % chat_id)
      return 0
  except Exception:
    logging.error('some problems with %s' % chat_id)
    return 1
  
def delSubscriber(chat_id):
  try:
    if os.path.exists(user_db):
      subscribers = open(user_db).read()
      if str(chat_id) in subscribers:
        new_user_db = open(user_db,"w")
        new_user_db.write(re.sub(str(chat_id) + '\n','',subscribers))
        new_user_db.close()
        logging.info('%s is deleted' % chat_id)
        return 0
      else:
        return 3
        logging.info('no such user: %s' % chat_id)
        pass
    else:                                       # db does not exist
      new_user_db = open(user_db,"w")
      new_user_db.close()
      return 3
      logging.info('no such user: %s' % chat_id)
  except Exception:
    logging.error('some problems with %s' % chat_id)
    return 1
  
def echo(bot, update_id):                                                       # Request updates after the last update_id
    for update in bot.getUpdates(offset=update_id, timeout=10):                 # chat_id is required to reply to any message
        chat_id = update.message.chat_id
        update_id = update.update_id + 1
        message = update.message.text

        if message == "/start":                                                 # Reply to the start message
            if addSubscriber(chat_id) == 0:
              bot.sendMessage(chat_id=chat_id,
                            text="Привет! Вы подписаны на обновления vandrouki.")
            elif addSubscriber(chat_id) == 4:
              bot.sendMessage(chat_id=chat_id,
                            text="Вы ведь уже подписаны на обновления vandrouki!")
            else:
              bot.sendMessage(chat_id=chat_id,
                            text="У нас что-то пошло не так...")
        elif message == "/stop":                                                # Reply to the message
            if delSubscriber(chat_id) == 0:
              bot.sendMessage(chat_id=chat_id,
                              text="Вы отписались от обновления vandrouki. Пока!")
            elif delSubscriber(chat_id) == 3:
              bot.sendMessage(chat_id=chat_id,
                              text="Привет! А Вы не подписаны на обновления vandrouki.")
            else:
              bot.sendMessage(chat_id=chat_id,
                              text="У нас что-то пошло не так...")
        elif message:
          bot.sendMessage(chat_id=chat_id,
                              text="Что-что? Я понимаю только /start и /stop")

    return update_id

def getLastNews(amount):                                                                        # it works now with only one news
  try:
      num = 1
      page = urlopen(URL)
      soup = BeautifulSoup(page, "html.parser")
      with open(news, 'r') as file:
        for a in soup.findAll('a', { 'rel': 'bookmark' }):
          if num <= amount:
            news = a.get_text() + " (" + str(a.get('href')) + ")." + '\n'         # it looks like: "Example text (example link)."
            if news.encode('utf-8') == file.readline():                           # file and variable are the same, so no news
              pass
              return 0
            else:
              with open(news, 'w') as file:
                file.write(news.encode('utf-8'))
              return 0
              print('updated')
            num += 1
          else:
            break
  except Exception:
      logging.error('some problems with getLastNews()')
      return 1
  

if __name__ == '__main__':
    main()
