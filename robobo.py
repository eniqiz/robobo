#!/usr/bin/env python3
# -*-coding:utf-8-*-
"""
Simple telegram robot.
"""
from telegram.ext import Updater, CommandHandler
from bs4 import BeautifulSoup
import requests
import html
import re
import psycopg2
import logging
import config


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')


def start(bot, update):
    """
    Welcome reply after start bot.
    """
    update.message.reply_text('Hi~')


def ping(bot, update):
    """
    Are you there?
    """
    update.message.reply_text('I am still alive.')


def tracker(bot, update, args):
    """
    Query debian package tracker.
    """
    chat_id = update.message.chat.id
    try:
        pkg_name = args[0]
    except IndexError:
        answer = '你要告诉我你要找什么噢~\n`/tracker@ouobot 包名`'
        bot.sendMessage(chat_id=chat_id, text=answer, parse_mode='markdown')
        return
    pkg_url = 'https://tracker.debian.org/pkg/' + pkg_name
    response = requests.get(pkg_url)
    if response.status_code == 404:
        answer = '好像木有找到这个包'
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        # set package tracker link for the package
        answer = '*Package:* [' + soup.body.h1.get_text() + ']'
        answer = answer + '(' + pkg_url + ')\n'

        ver_element = soup.find(text=re.compile('.*versions.*'))
        if ver_element is None:
            answer = '这个包好像已经被吃掉了'
        else:
            tmp = ver_element.find_parent(class_='panel-heading')
            tmp = tmp.find_next_sibling(class_='panel-body')
            vers = tmp.find_all('li')
            for i in vers:
                ver_num = i.a.get_text().strip()
                if not any(char.isdigit() for char in ver_num):
                    ver_num = i.span.next_sibling.next_sibling.get_text().strip()
                answer = answer + '*' + \
                    i.b.get_text() + '* ' + ver_num
                answer = answer + '\n'
    bot.sendMessage(chat_id=chat_id, text=answer, parse_mode='markdown')

def pkg(bot, update, args):
    """
    Query debian package versions from udd mirror
    """
    chat_id = update.message.chat.id
    try:
        pkg_name = args[0]
    except IndexError:
        answer = '你要告诉我你要找什么噢~\n`/pkg@ouobot 包名`'
        bot.sendMessage(chat_id=chat_id, text=answer, parse_mode='markdown')
        return
    conn = psycopg2.connect("dbname=udd user=udd-mirror password=udd-mirror host=udd-mirror.debian.net port=5432")
    cur = conn.cursor()
    cur.execute("SELECT version, release FROM packages_summary WHERE package = '" + pkg_name +"'")
    records = cur.fetchall()
    conn.close()
    if len(records) == 0:
        answer = '没有找到你想要的哦'
    else:
        answer = '*Package:* ' + pkg_name + '\n-------------------------------\n'
        for i in records:
            answer = answer + '*' + i[1] +':* ' + i[0] +'\n'
    bot.sendMessage(chat_id=chat_id, text=answer, parse_mode='markdown')


def bug_url(bot, update, args):
    """
    return debian bug page url.
    """
    try:
        bug_id = args[0]
    except IndexError:
        return
    if bug_id.isdigit():
        url_prefix = 'https://bugs.debian.org/cgi-bin/bugreport.cgi?bug='
        bug_url = url_prefix + bug_id
        response = requests.get(bug_url)
        if response.status_code == 404:
            answer = '好像木有这个 bug'
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            answer = soup.body.h1.text
            tmp = answer.split('\n')
            tmp[0] = '<b>' + tmp[0][:-3] + '</b>'
            tmp[1] = '<a href=\"' + bug_url + '\">' + tmp[1] + '</a>'
            answer = tmp[0] + '\n' + tmp[1] + '\n' + html.escape(tmp[2])
        update.message.reply_text(answer, quote=False,  parse_mode='html')
    else:
        update.message.reply_text('不要用奇怪的东西调戏我啊喂', quote=False)


updater = Updater(config.TOKEN)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('ping', ping))
updater.dispatcher.add_handler(CommandHandler('tracker', tracker,
                                              pass_args=True))
updater.dispatcher.add_handler(CommandHandler('bug', bug_url,
                                              pass_args=True))
updater.dispatcher.add_handler(CommandHandler('pkg', pkg,
                                              pass_args=True))

updater.start_webhook(listen='127.0.0.1', port=5000, url_path=config.TOKEN)
updater.bot.set_webhook("https://your_domain.com/" + config.TOKEN)
updater.idle()
