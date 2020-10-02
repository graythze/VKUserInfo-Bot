#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import telebot
import vk
import settings
import time
import urllib.request
import re
import traceback
from telebot import util
from datetime import datetime

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

session = vk.Session(access_token=settings.VK_TOKEN)
api = vk.API(session, v='5.124', lang='ru', timeout=10)


def find_at(msg):
    for text in msg:
        if text in text:
            return text


def timer():
    time.sleep(0.35)


def get_country_str(*country):
    country_str = api.database.getCountriesById(
        country_ids=country)
    return country_str


def get_city_str(*city):
    city_str = api.database.getCitiesById(
        city_ids=city)
    return city_str


@bot.message_handler(commands=['start'])
def regular_message(message):
    bot.send_message(message.from_user.id, "<b>Welcome to bot! 🤖</b>\n"
                                           "\nPlease send the user's ID page 🔎"
                                           '\n(eg. "<b>durov</b>" or "<b>id1</b>")', parse_mode="HTML")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.from_user.id, "Bot collects all main information (if available) from user's page."
                                           "To start, send a text message with ID to get info about the user.\n"
                                           "\n<b>DISCLAIMER: All data is taken from public sources by VK API's"
                                           "users.get Method.</b> "
                                           "\n<b>More at vk.com/dev/users.get</b>", parse_mode="HTML")


@bot.message_handler(func=lambda msg: msg.text is not None)
def get_info(message):
    try:
        got_text = message.text.split()
        at_text = find_at(got_text).lower()
        if len(re.findall(r'com/(.*)', at_text)) == 0:
            pass
        else:
            at_text = str(re.findall(r'com/(.*)', at_text))[2:-2]

        get_json = api.users.get(
            fields='photo_id, verified, sex, bdate, city, country, home_town, photo_max_orig, domain, wall_comments,'
                   'contacts, site, education, universities, schools, status, last_seen, followers_count, has_photo,'
                   'occupation, nickname, relatives, relation, personal, connections, exports, activities, interests,'
                   'music, movies, tv, books, games, about, quotes, can_post, can_see_all_posts, can_see_audio,'
                   'can_write_private_message, can_send_friend_request, screen_name, maiden_name, crop_photo, career,'
                   'can_be_invited_group, counters, military, is_closed', user_ids=at_text)

        data = {}

        if 'id' in get_json[0]:
            data["— ID"] = get_json[0]['id']

        if 'first_name' and 'last_name' in get_json[0]:
            data["— Name"] = get_json[0]['first_name'] + ' ' + get_json[0]['last_name']
        else:
            if 'first_name' in get_json[0]:
                if get_json[0]['first_name'] == "":
                    pass
                else:
                    data["— First name"] = get_json[0]['first_name']

            if 'last_name' in get_json[0]:
                if get_json[0]['last_name'] == "":
                    pass
                else:
                    data["— Last name"] = get_json[0]['last_name']

        if 'nickname' in get_json[0]:
            if get_json[0]['nickname'] == "":
                pass
            else:
                data["— Middle name"] = get_json[0]['nickname']

        if 'maiden_name' in get_json[0]:
            if get_json[0]['maiden_name'] == "":
                pass
            else:
                data["— Maiden name"] = get_json[0]['maiden_name']

        if 'deactivated' in get_json[0]:
            if get_json[0]['deactivated'] == "deleted":
                data["— Page status"] = "Deleted"
            else:
                data["— Page status"] = "Blocked"

        if 'can_write_private_message' in get_json[0]:
            if 'deactivated' in get_json[0]:
                pass
            else:
                if get_json[0]["can_write_private_message"] == 0:
                    data["— PM"] = "Not allowed"
                else:
                    data["— PM"] = "Allowed"

        if 'is_closed' in get_json[0]:
            if not get_json[0]['is_closed']:
                data["— Page privacy"] = "Open"
                if 'can_see_all_posts' in get_json[0]:
                    if get_json[0]["can_see_all_posts"] == 0:
                        data["— All posts"] = "Hidden"
                    else:
                        data["— All posts"] = "Visible"

                if 'can_post' in get_json[0]:
                    if 'deactivated' in get_json[0]:
                        pass
                    else:
                        if get_json[0]["can_post"] == 0:
                            data["— Posting"] = "Not allowed"
                        else:
                            data["— Posting"] = "Allowed"

                if 'can_see_audio' in get_json[0]:
                    if get_json[0]["can_see_audio"] == 0:
                        data["— Audio"] = "Hidden"
                    else:
                        data["— Audio"] = "Visible"

                if 'wall_comments' in get_json[0]:
                    if get_json[0]['wall_comments'] == 1:
                        data["— Commenting"] = "Allowed"
                    else:
                        data["— Commenting"] = "Not allowed"
            else:
                data["— Page privacy"] = "Closed"

        if 'can_send_friend_request' in get_json[0]:
            if get_json[0]["can_send_friend_request"] == 0:
                data["— Friend request"] = "Not allowed"
            else:
                data["— Friend request"] = "Allowed"

        if 'sex' in get_json[0]:
            if 'first_name' in get_json[0]:
                if get_json[0]['first_name'] == "DELETED":
                    pass
                else:
                    if get_json[0]['sex'] == 1:
                        data["— Sex"] = 'Female'
                    if get_json[0]['sex'] == 2:
                        data["— Sex"] = 'Male'

        if 'verified' in get_json[0]:
            if get_json[0]['verified'] == 1:
                data["— Verified"] = "Yes"

        if 'bdate' in get_json[0]:
            data["— Birthday"] = get_json[0]['bdate']

        if 'military' in get_json[0]:
            if len(get_json[0]["military"]) == 0:
                pass
            else:
                data['— Military'] = {}
                x = 0
                for i in get_json[0]["military"]:
                    if 'unit' in i:
                        data["— Military"]["#" + str(x + 1) + ", " + i['unit']] = {}
                    if 'country_id' in i:
                        data["— Military"]["#" + str(x + 1) + ", " + i['unit']]['Country'] = \
                            get_country_str(i['country_id'])[0]['title']
                        timer()
                    if 'from' and 'until' in i:
                        data["— Military"]["#" + str(x + 1) + ", " + i['unit']]['Time'] = str(i['from']) + ' — ' + str(
                            i['until'])
                    else:
                        if 'from' in i:
                            data["— Military"]["#" + str(x + 1) + ", " + i['unit']]['From'] = i['from']
                        if 'until' in i:
                            data["— Military"]["#" + str(x + 1) + ", " + i['unit']]['Until'] = i['until']
                    x += 1

        if 'relation' in get_json[0]:
            if get_json[0]['relation'] == 0:
                pass
            else:
                data["— Relationship"] = {}
                if get_json[0]['relation'] == 1:
                    data["— Relationship"]["Status"] = "Single"
                elif get_json[0]['relation'] == 2:
                    data["— Relationship"]["Status"] = "In a relationship"
                elif get_json[0]['relation'] == 3:
                    data["— Relationship"]["Status"] = "Engaged"
                elif get_json[0]['relation'] == 4:
                    data["— Relationship"]["Status"] = "Married"
                elif get_json[0]['relation'] == 5:
                    data["— Relationship"]["Status"] = "Complicated"
                elif get_json[0]['relation'] == 6:
                    data["— Relationship"]["Status"] = "Searching"
                elif get_json[0]['relation'] == 7:
                    data["— Relationship"]["Status"] = "In love"
                elif get_json[0]['relation'] == 8:
                    data["— Relationship"]["Status"] = "In a civil union"

            if 'relation_partner' in get_json[0]:
                for i in get_json[0]['relation_partner']:
                    data["— Relationship"]["Partner ID"] = "vk.com/id" + str(i['id'])
                    if 'first_name' and 'last_name' in i:
                        data["— Relationship"]["Name"] = i["first_name"] + ' ' + i["last_name"]
                    else:
                        if 'first_name' in i:
                            data["— Relationship"]["First name"] = i["first_name"]
                        if 'last_name' in i:
                            data["— Relationship"]["Last name"] = i["last_name"]

        if 'relatives' in get_json[0]:
            if len(get_json[0]["relatives"]) == 0:
                pass
            else:
                data["— Relatives"] = {}
                relatives = []
                for i in get_json[0]["relatives"]:
                    if i["id"] < 0:
                        if 'id' and 'name' in i:
                            relatives.append(i["type"].capitalize() + ": " + i['name'])
                        else:
                            relatives.append(i["type"].capitalize() + ":" + " no link")
                    else:
                        relatives.append(i["type"].capitalize() + ":" + " vk.com/id" + str(i['id']))
                data["— Relatives"] = relatives

        if 'schools' in get_json[0]:
            if len(get_json[0]["schools"]) == 0:
                pass
            else:
                data['— Schools'] = {}
                x = 0
                for i in get_json[0]["schools"]:
                    if 'name' in i:
                        data['— Schools']["#" + str(x + 1) + ", " + i['name']] = {}

                    if 'country' and 'city' in i:
                        country_str = get_country_str(i['country'])[0]['title']
                        timer()
                        city_str = get_city_str(i['city'])[0]['title']
                        timer()
                        data['— Schools']["#" + str(x + 1) + ", " + i['name']]['Place'] = str(country_str) + ', ' + str(
                            city_str)
                    else:
                        if 'country' in i:
                            data['— Schools']["#" + str(x + 1) + ", " + i['name']]['Country'] = \
                                get_country_str(i['country'])[0]['title']
                            timer()
                        if 'city' in i:
                            data['— Schools']["#" + str(x + 1) + ", " + i['name']]['City'] = get_city_str(i['city'])[0][
                                'title']
                            timer()

                    if 'year_from' and 'year_to' in i:
                        data['— Schools']["#" + str(x + 1) + ", " + i['name']]['Studying'] = str(
                            i['year_from']) + ' — ' + str(i['year_to'])
                    else:
                        if 'year_from' in i:
                            data['— Schools']["#" + str(x + 1) + ", " + i['name']]['From'] = i['year_from']
                        if 'year_to' in i:
                            data['— Schools']["#" + str(x + 1) + ", " + i['name']]['To'] = i['year_to']
                    if 'year_graduated' in i:
                        data['— Schools']["#" + str(x + 1) + ", " + i['name']]['Graduated'] = i['year_graduated']
                    if 'class' in i:
                        if i['class'] == "":
                            pass
                        else:
                            data['— Schools']["#" + str(x + 1) + ", " + i['name']]['Class'] = i['class']
                    if 'speciality' in i:
                        data['— Schools']["#" + str(x + 1) + ", " + i['name']]['Speciality'] = i['speciality']
                    if 'type_str' in i:
                        data['— Schools']["#" + str(x + 1) + ", " + i['name']]['Type'] = i['type_str']
                    x += 1

        if 'career' in get_json[0]:
            if len(get_json[0]["career"]) == 0:
                pass
            else:
                data["— Career"] = {}
                x = 0
                for i in get_json[0]["career"]:
                    if 'group_id' in i:
                        data["— Career"]["#" + str(x + 1) + ", " + 'vk.com/public' + str(i['group_id'])] = {}
                        if 'country_id' and 'city_id' in i:
                            country_str = get_country_str(i['country_id'])[0]['title']
                            timer()
                            city_str = get_city_str(i['city_id'])[0]['title']
                            timer()
                            data["— Career"]["#" + str(x + 1) + ", " + 'vk.com/public' + str(i['group_id'])][
                                'Place'] = str(country_str) + ', ' + str(city_str)
                        else:
                            if 'country_id' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + 'vk.com/public' + str(i['group_id'])][
                                    'Country'] = get_country_str(i['country_id'])[0]['title']
                                timer()
                            if 'city_id' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + 'vk.com/public' + str(i['group_id'])][
                                    'City'] = get_city_str(i['city_id'])[0]['title']
                                timer()

                        if 'from' and 'until' in i:
                            data["— Career"]["#" + str(x + 1) + ", " + 'vk.com/public' + str(i['group_id'])][
                                'Period'] = str(i['from']) + ' — ' + str(i['until'])
                        else:
                            if 'from' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + 'vk.com/public' + str(i['group_id'])][
                                    'From'] = i['from']
                            if 'until' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + 'vk.com/public' + str(i['group_id'])]['To'] = \
                                    i['until']
                        if 'position' in i:
                            data["— Career"]["#" + str(x + 1) + ", " + 'vk.com/public' + str(i['group_id'])][
                                'Position'] = i['position']

                    if 'company' in i:
                        data["— Career"]["#" + str(x + 1) + ", " + i['company']] = {}

                        if 'country_id' and 'city_id' in i:
                            country_str = get_country_str(i['country_id'])[0]['title']
                            timer()
                            city_str = get_city_str(i['city_id'])[0]['title']
                            timer()
                            data["— Career"]["#" + str(x + 1) + ", " + i['company']]['Place'] = str(
                                country_str) + ', ' + str(city_str)
                        else:
                            if 'country_id' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + i['company']]['Country'] = \
                                    get_country_str(i['country_id'])[0]['title']
                                timer()
                            if 'city_id' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + i['company']]['City'] = \
                                    get_city_str(i['city_id'])[0]['title']
                                timer()

                        if 'from' and 'until' in i:
                            data["— Career"]["#" + str(x + 1) + ", " + i['company']]['Period'] = str(
                                i['from']) + ' — ' + str(i['until'])
                        else:
                            if 'from' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + i['company']]['From'] = i['from']
                            if 'until' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + i['company']]['To'] = i['until']
                        if 'position' in i:
                            data["— Career"]["#" + str(x + 1) + ", " + i['company']]['Position'] = i['position']
                    x += 1

        if 'site' in get_json[0]:
            if get_json[0]['site'] == "":
                pass
            else:
                data["— Site"] = get_json[0]["site"]

        if 'last_seen' in get_json[0]:
            if 'time' in get_json[0]["last_seen"]:
                data["— Last seen"] = datetime.utcfromtimestamp(get_json[0]["last_seen"]["time"]).strftime(
                    '%Y-%m-%d %H:%M:%S')
            if 'platform' in get_json[0]["last_seen"]:
                if get_json[0]["last_seen"]["platform"] == 1:
                    data["— Platform"] = "m.vk.com"
                if get_json[0]["last_seen"]["platform"] == 2:
                    data["— Platform"] = "iPhone"
                if get_json[0]["last_seen"]["platform"] == 3:
                    data["— Platform"] = "iPad"
                if get_json[0]["last_seen"]["platform"] == 4:
                    data["— Platform"] = "Android"
                if get_json[0]["last_seen"]["platform"] == 5:
                    data["— Platform"] = "Windows Phone"
                if get_json[0]["last_seen"]["platform"] == 6:
                    data["— Platform"] = "Windows 8"
                if get_json[0]["last_seen"]["platform"] == 7:
                    data["— Platform"] = "vk.com"
        else:
            if "deactivated" in get_json[0]:
                pass
            else:
                data["— Platform"] = "vk.me/app"
                data["— Last seen"] = "Hidden"

        if 'status' in get_json[0]:
            if get_json[0]["status"] == "":
                pass
            else:
                data["— Status"] = get_json[0]["status"]

        if 'occupation' in get_json[0]:
            if 'name' in get_json[0]["occupation"]:
                data['— Occupation'] = {}
                data['— Occupation']["Place"] = get_json[0]["occupation"]["name"]
            if 'type' in get_json[0]["occupation"]:
                data['— Occupation']["Type"] = get_json[0]["occupation"]["type"]

        if 'screen_name' in get_json[0]:
            data["— Domain"] = get_json[0]["screen_name"]

        if 'activities' in get_json[0]:
            if get_json[0]["activities"] == "":
                pass
            else:
                data["— Activities"] = get_json[0]["activities"]

        if 'interests' in get_json[0]:
            if get_json[0]["interests"] == "":
                pass
            else:
                data["— Interests"] = get_json[0]["interests"]

        if 'music' in get_json[0]:
            if get_json[0]["music"] == "":
                pass
            else:
                data["— Music"] = get_json[0]["music"]

        if 'movies' in get_json[0]:
            if get_json[0]["movies"] == "":
                pass
            else:
                data["— Movies"] = get_json[0]["movies"]

        if 'tv' in get_json[0]:
            if get_json[0]["tv"] == "":
                pass
            else:
                data["— TV"] = get_json[0]["tv"]

        if 'books' in get_json[0]:
            if get_json[0]["books"] == "":
                pass
            else:
                data["— Books"] = get_json[0]["books"]

        if 'games' in get_json[0]:
            if get_json[0]["games"] == "":
                pass
            else:
                data["— Games"] = get_json[0]["games"]

        if 'about' in get_json[0]:
            if get_json[0]["about"] == "":
                pass
            else:
                data["— About"] = get_json[0]["about"]

        if 'quotes' in get_json[0]:
            if get_json[0]["quotes"] == "":
                pass
            else:
                data["— Quotes"] = get_json[0]["quotes"]

        if 'counters' in get_json[0]:
            data["— Number of"] = {}

            if 'albums' in get_json[0]["counters"]:
                if get_json[0]["counters"]["albums"] == 0:
                    pass
                else:
                    data["— Number of"]["Albums"] = get_json[0]["counters"]["albums"]

            if 'videos' in get_json[0]["counters"]:
                if get_json[0]["counters"]["videos"] == 0:
                    pass
                else:
                    data["— Number of"]["Videos"] = get_json[0]["counters"]["videos"]

            if 'audios' in get_json[0]["counters"]:
                if get_json[0]["counters"]["audios"] == 0:
                    pass
                else:
                    data["— Number of"]["Audios"] = get_json[0]["counters"]["audios"]

            if 'photos' in get_json[0]["counters"]:
                if get_json[0]["counters"]["photos"] == 0:
                    pass
                else:
                    data["— Number of"]["Photos"] = get_json[0]["counters"]["photos"]

            if 'notes' in get_json[0]["counters"]:
                if get_json[0]["counters"]["notes"] == 0:
                    pass
                else:
                    data["— Number of"]["Notes"] = get_json[0]["counters"]["notes"]

            if 'friends' in get_json[0]["counters"]:
                if get_json[0]["counters"]["friends"] == 0:
                    pass
                else:
                    data["— Number of"]["Friends"] = get_json[0]["counters"]["friends"]

            if 'groups' in get_json[0]["counters"]:
                if get_json[0]["counters"]["groups"] == 0:
                    pass
                else:
                    data["— Number of"]["Groups"] = get_json[0]["counters"]["groups"]

            if 'posts' in get_json[0]["counters"]:
                if get_json[0]["counters"]["posts"] == 0:
                    pass
                else:
                    data["— Number of"]["Posts"] = get_json[0]["counters"]["posts"]

            if 'gifts' in get_json[0]["counters"]:
                if get_json[0]["counters"]["gifts"] == 0:
                    pass
                else:
                    data["— Number of"]["Gifts"] = get_json[0]["counters"]["gifts"]

            if 'user_videos' in get_json[0]["counters"]:
                if get_json[0]["counters"]["user_videos"] == 0:
                    pass
                else:
                    data["— Number of"]["User's tagged video"] = get_json[0]["counters"]["user_video"]

            if 'followers' in get_json[0]["counters"]:
                if get_json[0]["counters"]["followers"] == 0:
                    pass
                else:
                    data["— Number of"]["Followers"] = get_json[0]["counters"]["followers"]

            if 'user_photos' in get_json[0]["counters"]:
                if get_json[0]["counters"]["user_photos"] == 0:
                    pass
                else:
                    data["— Number of"]["User's tagged photos"] = get_json[0]["counters"]["user_photos"]

            if 'subscriptions' in get_json[0]["counters"]:
                if get_json[0]["counters"]["subscriptions"] == 0:
                    pass
                else:
                    data["— Number of"]["Subscriptions"] = get_json[0]["counters"]["subscriptions"]

            if 'pages' in get_json[0]["counters"]:
                if get_json[0]["counters"]["pages"] == 0:
                    pass
                else:
                    data["— Number of"]["Pages"] = get_json[0]["counters"]["pages"]

            if len(data["— Number of"]) == 0:
                del data["— Number of"]

        if 'personal' in get_json[0]:
            data["— Personal"] = {}
            if 'political' in get_json[0]["personal"]:
                if get_json[0]["personal"]["political"] == 1:
                    data["— Personal"]["Political"] = "Communist"
                elif get_json[0]["personal"]["political"] == 2:
                    data["— Personal"]["Political"] = "Socialist"
                elif get_json[0]["personal"]["political"] == 3:
                    data["— Personal"]["Political"] = "Moderate"
                elif get_json[0]["personal"]["political"] == 4:
                    data["— Personal"]["Political"] = "Liberal"
                elif get_json[0]["personal"]["political"] == 5:
                    data["— Personal"]["Political"] = "Conservative"
                elif get_json[0]["personal"]["political"] == 6:
                    data["— Personal"]["Political"] = "Monarchist"
                elif get_json[0]["personal"]["political"] == 7:
                    data["— Personal"]["Political"] = "Ultraconservative"
                elif get_json[0]["personal"]["political"] == 8:
                    data["— Personal"]["Political"] = "Apathetic"
                elif get_json[0]["personal"]["political"] == 9:
                    data["— Personal"]["Political"] = "Libertian"

            if 'langs' in get_json[0]["personal"]:
                langs = ', '.join(map(str, get_json[0]["personal"]["langs"]))
                data["— Personal"]["Languages"] = langs

            if 'religion' in get_json[0]["personal"]:
                data["— Personal"]["Religion"] = get_json[0]["personal"]["religion"]

            if 'inspired_by' in get_json[0]["personal"]:
                data["— Personal"]["Inspired by"] = get_json[0]["personal"]["inspired_by"]

            if 'people_main' in get_json[0]["personal"]:
                if get_json[0]["personal"]["people_main"] == 1:
                    data["— Personal"]["People main"] = "Intellect and creativity"
                elif get_json[0]["personal"]["people_main"] == 2:
                    data["— Personal"]["People main"] = "Kindness and honesty"
                elif get_json[0]["personal"]["people_main"] == 3:
                    data["— Personal"]["People main"] = "Health and beauty"
                elif get_json[0]["personal"]["people_main"] == 4:
                    data["— Personal"]["People main"] = "Wealth and power"
                elif get_json[0]["personal"]["people_main"] == 5:
                    data["— Personal"]["People main"] = "Courage and persistance"
                elif get_json[0]["personal"]["people_main"] == 6:
                    data["— Personal"]["People main"] = "Humor and love for life"

            if 'life_main' in get_json[0]["personal"]:
                if get_json[0]["personal"]["life_main"] == 1:
                    data["— Personal"]["Life main"] = "Family and children"
                elif get_json[0]["personal"]["life_main"] == 2:
                    data["— Personal"]["Life main"] = "Career and money"
                elif get_json[0]["personal"]["life_main"] == 3:
                    data["— Personal"]["Life main"] = "Entertainment and leisure"
                elif get_json[0]["personal"]["life_main"] == 4:
                    data["— Personal"]["Life main"] = "Science and research"
                elif get_json[0]["personal"]["life_main"] == 5:
                    data["— Personal"]["Life main"] = "Improving the world"
                elif get_json[0]["personal"]["life_main"] == 6:
                    data["— Personal"]["Life main"] = "Personal development"
                elif get_json[0]["personal"]["life_main"] == 7:
                    data["— Personal"]["Life main"] = "Beauty and art"
                elif get_json[0]["personal"]["life_main"] == 8:
                    data["— Personal"]["Life main"] = "Fame and influence"

            if 'smoking' in get_json[0]["personal"]:
                if get_json[0]["personal"]["smoking"] == 1:
                    data["— Personal"]["Smoking"] = "Very negative"
                elif get_json[0]["personal"]["smoking"] == 2:
                    data["— Personal"]["Smoking"] = "Negative"
                elif get_json[0]["personal"]["smoking"] == 3:
                    data["— Personal"]["Smoking"] = "Neutral"
                elif get_json[0]["personal"]["smoking"] == 4:
                    data["— Personal"]["Smoking"] = "Compromisable"
                elif get_json[0]["personal"]["smoking"] == 5:
                    data["— Personal"]["Smoking"] = "Positive"

            if 'alcohol' in get_json[0]["personal"]:
                if get_json[0]["personal"]["alcohol"] == 1:
                    data["— Personal"]["Alcohol"] = "Very negative"
                elif get_json[0]["personal"]["alcohol"] == 2:
                    data["— Personal"]["Alcohol"] = "Negative"
                elif get_json[0]["personal"]["alcohol"] == 3:
                    data["— Personal"]["Alcohol"] = "Neutral"
                elif get_json[0]["personal"]["alcohol"] == 4:
                    data["— Personal"]["Alcohol"] = "Compromisable"
                elif get_json[0]["personal"]["alcohol"] == 5:
                    data["— Personal"]["Alcohol"] = "Positive"

        if 'mobile_phone' in get_json[0]:
            if len(get_json[0]["mobile_phone"]) == 0:
                pass
            else:
                data["— Mobile"] = get_json[0]["mobile_phone"]

        if 'home_phone' in get_json[0]:
            if len(get_json[0]["home_phone"]) == 0:
                pass
            else:
                data["— Home phone"] = get_json[0]["home_phone"]

        if 'skype' in get_json[0]:
            data["— Skype"] = get_json[0]["skype"]

        if 'instagram' in get_json[0]:
            data["— Instagram"] = "@" + get_json[0]["instagram"]

        if 'twitter' in get_json[0]:
            data["— Twitter"] = "@" + get_json[0]["twitter"]

        if 'livejournal' in get_json[0]:
            data["— LiveJournal"] = "@" + get_json[0]["livejournal"]

        if 'facebook' in get_json[0]:
            data["— Facebook"] = "facebook.com/profile.php?id=" + get_json[0]["facebook"]

        if 'country' and 'city' in get_json[0]:
            if 'title' in get_json[0]["country"] and 'title' in get_json[0]["city"]:
                data["— Location"] = get_json[0]["country"]["title"] + ', ' + get_json[0]["city"]["title"]
        else:
            if 'country' in get_json[0]:
                if 'title' in get_json[0]["country"]:
                    data["— Country"] = get_json[0]["country"]["title"]

            if 'city' in get_json[0]:
                if 'title' in get_json[0]["city"]:
                    data["— City"] = get_json[0]["city"]["title"]

        if 'home_town' in get_json[0]:
            if get_json[0]["home_town"] == "":
                pass
            else:
                data["— Hometown"] = get_json[0]["home_town"]

        try:
            link = settings.FOAF_LINK + str(get_json[0]['id'])
            with urllib.request.urlopen(link) as response:
                parsed_xml = str(re.findall(r'ya:created dc:date="(.*)"', response.read().decode("windows-1251")))
            if len(parsed_xml) > 2:
                data["— Registered"] = parsed_xml[2:-8].replace('T', " ")
        except:
            pass

        if 'has_photo' in get_json[0]:
            if get_json[0]['has_photo'] == 0:
                pass
            else:
                if 'crop_photo' in get_json[0]:
                    if 'photo' in get_json[0]["crop_photo"]:
                        full_size_ava = max(get_json[0]["crop_photo"]["photo"]['sizes'],
                                            key=lambda line: int(line['width']))
                        data["— Avatar"] = full_size_ava['url']
                    if 'date' in get_json[0]["crop_photo"]["photo"]:
                        data["— Avatar date"] = datetime.utcfromtimestamp(
                            get_json[0]["crop_photo"]["photo"]["date"]).strftime('%Y-%m-%d %H:%M:%S')

        if 'universities' in get_json[0]:
            if len(get_json[0]["universities"]) == 0:
                pass
            else:
                data["— Education"] = {}
                x = 0
                for i in get_json[0]["universities"]:
                    if 'name' in i:
                        data["— Education"]["#" + str(x + 1) + ", " + i['name']] = {}
                    if 'country' and 'city' in i:
                        if i['country'] == 0 and i['city'] == 0:
                            pass
                        else:
                            country_str = get_country_str(i['country'])[0]['title']
                            timer()
                            city_str = get_city_str(i['city'])[0]['title']
                            timer()
                            data["— Education"]["#" + str(x + 1) + ", " + i['name']][
                                "Place"] = country_str + ', ' + city_str
                    else:
                        if 'country' in i:
                            if i['country'] == 0:
                                pass
                            else:
                                data["— Education"]["#" + str(x + 1) + ", " + i['name']]["Country"] = \
                                    get_country_str(i['country'])[0]['title']
                                timer()
                        if 'city' in i:
                            if i['city'] == 0:
                                pass
                            else:
                                data["— Education"]["#" + str(x + 1) + ", " + i['name']]["City"] = \
                                    get_city_str(i['city'])[0]['title']
                                timer()

                    if 'faculty_name' in i:
                        data["— Education"]["#" + str(x + 1) + ", " + i['name']]["Faculty"] = i['faculty_name']
                    if 'chair_name' in i:
                        data["— Education"]["#" + str(x + 1) + ", " + i['name']]["Study program"] = i['chair_name']
                    if 'graduation' in i:
                        data["— Education"]["#" + str(x + 1) + ", " + i['name']]["Graduation"] = i['graduation']
                    if 'education_form' in i:
                        data["— Education"]["#" + str(x + 1) + ", " + i['name']]["Form"] = i['education_form']
                    if 'education_status' in i:
                        data["— Education"]["#" + str(x + 1) + ", " + i['name']]["Status"] = i['education_status']
                    x += 1

        def serialize(dct, tabs=0):
            rslt = []
            pref = ' ' * tabs
            for k, v in dct.items():
                if isinstance(v, dict):
                    rslt += [pref + str(k) + ':']
                    rslt += [serialize(v, tabs + 2)]
                elif isinstance(v, list):
                    rslt += [pref + str(k) + ': ']
                    for x in range(len(v)):
                        rslt += [' ' * 2 + v[x]]
                else:
                    rslt += [pref + str(k) + ': ' + str(v)]
            return '\n'.join(rslt)

        result = serialize(data)
        for i in settings.TO_REMOVE:
            result = result.replace(i, '')

        ready_text = util.split_string(result, 4096)

        bot.send_message(message.from_user.id, "⌛ Requested info for " + at_text + " on " + str(
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")) + " UTC")

        for text in ready_text:
            bot.send_message(message.from_user.id, text)


    except:
        bot.send_message(message.from_user.id, "<b>⚠️ Something went wrong. The reasons are:</b>\n"
                                               "1. Wrong user ID\n"
                                               "2. ID contains non Latin characters\n"
                                               "3. ID contains special characters (e.g. comma, tilde)",
                         parse_mode="HTML")
        traceback.print_exc()


while True:
    try:
        bot.polling(none_stop=True)
    except:
        traceback.print_exc()
        time.sleep(15)
