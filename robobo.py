#!/usr/bin/env python3
# -*-coding:utf-8-*-
"""
Simple telegram robot.
"""
import telegram
from flask import Flask, request
import logging
from bs4 import BeautifulSoup
import requests
import re
import config


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')

bot_name = '@Robobooooooooo_bot'
bot = telegram.Bot(token=config.TOKEN)
bot.setWebhook('https://bot.memo.ink/' + config.TOKEN)


@app.route('/')
def index():
    return '{"roborobo":"!"}'


@app.route('/<token>', methods=['POST'])
def launcher(token):
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        logging.info('I am still alive.')
        handle_message(update.message)
    return 'ok'


def handle_message(message):
    if message is None:
        return
    text = message.text
    if '御坂御坂' in text:
        ping(message)
    logging.info(text)
    if '/pkgver' in text:
        pkgver(message)


def ping(message):
    chat_id = message.chat.id
    bot.sendMessage(chat_id=chat_id, text='略略略')


def pkgver(message):
    chat_id = message.chat.id
    try:
        pkg_name = message.text.split(' ')[1]
    except IndexError:
        return
    response = requests.get('https://tracker.debian.org/pkg/' + pkg_name)
    if response.status_code == 404:
        answer = '好像木有找到这个包'
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        answer = soup.body.h1.contents[0] + '\n'
        ver_element = soup.find(text=re.compile('.*versions.*'))
        if ver_element is None:
            answer = '这个包好像已经被吃掉了'
        else:
            tmp = ver_element.find_parent(class_='panel-heading')
            tmp = tmp.find_next_sibling(class_='panel-body')
            vers = tmp.find_all('li')
            for i in vers:
                answer = answer + i.b.contents[0] + ' ' + i.a.contents[0]
                answer = answer + '\n'
    bot.sendMessage(chat_id=chat_id, text=answer)


if __name__ == "__main__":
    app.run()
