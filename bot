#!/usr/bin/env python
# -*- coding: utf-8 -*-

#

import logging
import telegram
from time import sleep
import re, os

import threading
#from multiprocessing import Process
from bs4 import BeautifulSoup
#from urllib.request import urlopen
from urllib import urlopen

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError  # python 2

subscribers_list = 'subscribers'
TIMEOUT = 30
URL = "http://vandrouki.ru"

def main():
  bot = telegram.Bot('154434670:AAFwtLfx_1fpfKPwYilDT1yO_yCjqC6SsEU')

  # get the first pending update_id, this is so we can skip over it in case
  # we get an "Unauthorized" exception.
  try:
      update_id = bot.getUpdates()[0].update_id
  except IndexError:
      update_id = None

  logging.basicConfig(
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  
  def notificateUser():
    while True:
        if getLastNews(1) == 0:
            with open(subscribers_list,'r') as file:
                for subscriber in file.read().splitlines():
                    bot.sendMessage(chat_id=subscriber,
                          text=open('last_news', 'r').read())
                    print('subscriber %s is notified' % subscriber)
        sleep(TIMEOUT)
  
  t = threading.Thread(target=notificateUser)
  t.daemon = True
  t.start()
  
  while True:
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
    if os.path.exists(subscribers_list):
      with open(subscribers_list,'r') as file:
        if str(chat_id) in file.read().splitlines():
          print('subscriber %s already in database' % chat_id)
          return 'already in database'
          pass
        else:
          with open(subscribers_list,'a') as file:
            file.write(str(chat_id) + '\n')
          print('done for %s' % chat_id)
          return 'done'
    else:
      with open(subscribers_list,'w') as file:
        file.write(str(chat_id) + '\n')
      print('done for %s' % chat_id)
      return 'done'
  except Exception:
    return 1
  
def delSubscriber(chat_id):
  try:
    if os.path.exists(subscribers_list):
      subscribers = open(subscribers_list).read()
      if str(chat_id) in subscribers:
        new_subscribers_list = open(subscribers_list,"w")
        new_subscribers_list.write(re.sub(str(chat_id) + '\n','',subscribers))
        new_subscribers_list.close()
        print('deletting done for %s' % chat_id)
        return('done')
      else:
        return('no such user')
        print('no such user: %s' % chat_id)
        pass
    else:
      new_subscribers_list = open(subscribers_list,"w")
      new_subscribers_list.close()
      return('no such user')
      print('no such user: %s', chat_id)
  except Exception:
    return 1
  
def echo(bot, update_id):                                                       # Request updates after the last update_id
    for update in bot.getUpdates(offset=update_id, timeout=10):                 # chat_id is required to reply to any message
        chat_id = update.message.chat_id
        update_id = update.update_id + 1
        message = update.message.text

        if message == "/start":                                                 # Reply to the start message
            if addSubscriber(chat_id) == "done":
              bot.sendMessage(chat_id=chat_id,
                            text="Привет! Вы подписаны на обновления vandrouki.")
            elif addSubscriber(chat_id) == "already in database":
              bot.sendMessage(chat_id=chat_id,
                            text="Вы ведь уже подписаны на обновления vandrouki!")
            else:
              bot.sendMessage(chat_id=chat_id,
                            text="У нас что-то пошло не так...")
              
        elif message == "/stop":                                                # Reply to the message
            if delSubscriber(chat_id) == 'done':
              bot.sendMessage(chat_id=chat_id,
                              text="Вы отписались от обновления vandrouki. Пока!")
            elif delSubscriber(chat_id) == 'no such user':
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
  num = 1
  page = urlopen(URL)
  soup = BeautifulSoup(page, "html.parser")
  with open('last_news', 'r') as file:
    for a in soup.findAll('a', { 'rel': 'bookmark' }):
      if num <= amount:
        news = a.get_text() + " (" + str(a.get('href')) + ")." + '\n'         # it looks like: "Example text (example link)."
        if news.encode('utf-8') == file.readline():                                                             # no news
          pass
          return 1
        else:
          with open('last_news', 'w') as file:
            file.write(news.encode('utf-8'))
          return 0
          print('updated')
        num += 1
      else:
        break
  

if __name__ == '__main__':
    main()
