#!/usr/bin/env python3
# -*-coding:utf-8-*-
"""
Simple telegram robot.
"""
import telegram
from flask import Flask, request
import logging
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
def launcher():
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


def ping(message):
    chat_id = message.chat.id
    bot.sendMessage(chat_id=chat_id, text='略略略')


if __name__ == "__main__":
    app.run()
