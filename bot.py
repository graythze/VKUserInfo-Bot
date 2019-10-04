#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import telebot
import vk
import settings
import time
import urllib.request
import re
from telebot import util
from datetime import datetime

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

session = vk.Session(access_token=settings.VK_TOKEN)
api = vk.API(session, v='5.101', lang='ru', timeout=10)


def find_at(msg):
    for text in msg:
        if text in text:
            return text


@bot.message_handler(commands=['start'])
def regular_message(message):
    bot.send_message(message.from_user.id, "<b>Welcome to bot! 🤖</b>\n"
                                           "\nPlease send ID of user's page below 🔎"
                                           '\n(eg. "<b>durov</b>" or "<b>id1</b>")', parse_mode="HTML")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.from_user.id, "This bot gets all information (if it's available) from user page. "
                                           "Just send text message with ID ang get info about it.\n"
                                           "\n<b>IMPORTANT: All data is taken from public sources by VK API by "
                                           "users.get method.</b> "
                                           "\n<b>More at vk.com/dev/users.get</b>", parse_mode="HTML")


@bot.message_handler(func=lambda msg: msg.text is not None)
def get_info(message):
    try:
        texts = message.text.split()
        at_text = find_at(texts)
        get_json = api.users.get(
            fields='photo_id, verified, sex, bdate, city, country, home_town, has_photo, photo_50, photo_100,'
                   'photo_200_orig, photo_200, photo_400_orig, photo_max, photo_max_orig, online, domain, has_mobile,'
                   'contacts, site, education, universities, schools, status, last_seen, followers_count,'
                   'occupation, nickname, relatives, relation, personal, connections, exports, activities, interests, '
                   'music, movies, tv, books, games, about, quotes, can_post, can_see_all_posts, can_see_audio,'
                   'can_write_private_message, can_send_friend_request, is_favorite, is_hidden_from_feed, timezone,'
                   'screen_name, maiden_name, crop_photo, career, military,'
                   'can_be_invited_group',
            user_ids=at_text.lower())

        '''parsing reg date'''
        link = settings.FOAF_LINK + str(get_json[0]['id'])
        with urllib.request.urlopen(link) as response:
            vk_xml = response.read().decode("windows-1251")

        parsed_xml = re.findall(r'ya:created dc:date="(.*)"', vk_xml)
        get_json[0].update({"reg_date": parsed_xml})
        ''' parsing reg date'''

        ready_json = json.dumps(get_json, indent=2, ensure_ascii=False)

        ''' replacing block '''
        for i in settings.TO_REMOVE:
            ready_json = ready_json.replace(i, '')
        ''' replacing block '''

        ready_text = util.split_string(ready_json, 4096)

        bot.send_message(message.from_user.id,
                         "⌛ Requested info for " + at_text.lower() + " on " + str(datetime.utcnow()) + " UTC")

        for text in ready_text:
            bot.send_message(message.from_user.id, text)


    except:
        bot.send_message(message.from_user.id, "<b>⚠️ Something gone wrong ;( There are some reasons:</b>\n"
                                               "1. Wrong user ID\n"
                                               "2. You typed ID with non-Latin text\n"
                                               "3. Non-usable signs, eg., comma or tilde\n", parse_mode="HTML")


while True:
    try:
        bot.polling(none_stop=True)
    except Exception:
        time.sleep(15)
