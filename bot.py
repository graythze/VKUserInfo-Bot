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
                                           "\nPlease send the user's ID page 🔎"
                                           '\n(eg. "<b>durov</b>" or "<b>id1</b>")', parse_mode="HTML")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.from_user.id, "This bot gets all information (if available) from user's page. "
                                           "Just send a text message with ID to get info about the user.\n"
                                           "\n<b>DISCLAIMER: All data is taken from public sources by VK API's "
                                           "users.get Method.</b> "
                                           "\n<b>More at vk.com/dev/users.get</b>", parse_mode="HTML")


@bot.message_handler(func=lambda msg: msg.text is not None)
def get_info(message):
    try:
        got_text = message.text.split()
        at_text = find_at(got_text)
        get_json = api.users.get(
            fields='photo_id, verified, sex, bdate, city, country, home_town, has_photo,'
                   'photo_max_orig, domain, has_mobile, wall_comments,'
                   'contacts, site, education, universities, schools, status, last_seen, followers_count,'
                   'occupation, nickname, relatives, relation, personal, connections, exports, activities, interests, '
                   'music, movies, tv, books, games, about, quotes, can_post, can_see_all_posts, can_see_audio,'
                   'can_write_private_message, can_send_friend_request,'
                   'screen_name, maiden_name, crop_photo, career, military,'
                   'can_be_invited_group, counters',
            user_ids=at_text.lower())

        data = {}

        try:
            data["— ID"] = get_json[0]['id']
        except:
            pass

        try:
            if get_json[0]['first_name'] == "":
                pass
            else:
                data["— First name"] = get_json[0]['first_name']
        except:
            pass

        try:
            if get_json[0]['last_name'] == "":
                pass
            else:
                data["— Last name"] = get_json[0]['last_name']
        except:
            pass

        try:
            if get_json[0]['nickname'] == "":
                pass
            else:
                data["— Middle name"] = get_json[0]['nickname']
        except:
            pass

        try:
            if get_json[0]['maiden_name'] == "":
                pass
            else:
                data["— Maiden name"] = get_json[0]['maiden_name']
        except:
            pass

        try:
            if get_json[0]['deactivated'] == "deleted":
                data["— Page status"] = "Deleted"
            else:
                data["— Page status"] = "Blocked"
        except:
            pass

        try:
            if get_json[0]['is_closed'] == "true":
                data["— Page status"] = "Hidden"
            else:
                data["— Page status"] = "Visible"
        except:
            pass

        try:
            if get_json[0]["can_write_private_message"] == 0:
                data["— PM"] = "Not allowed"
            else:
                data["— PM"] = "Allowed"
        except:
            pass

        try:
            if get_json[0]["can_see_all_posts"] == 0:
                data["— See all posts"] = "Not allowed"
            else:
                data["— See all posts"] = "Allowed"
        except:
            pass

        try:
            if get_json[0]["can_post"] == 0:
                data["— Posting"] = "Not allowed"
            else:
                data["— Posting"] = "Allowed"
        except:
            pass

        try:
            if get_json[0]["can_see_audio"] == 0:
                data["— Audio"] = "Not allowed"
            else:
                data["— Audio"] = "Allowed"
        except:
            pass

        try:
            if get_json[0]["can_send_friend_request"] == 0:
                data["— Friend request"] = "Not allowed"
            else:
                data["— Friend request"] = "Allowed"
        except:
            pass

        try:
            if get_json[0]['wall_comments'] == 1:
                data["— Commenting"] = "Allowed"
            else:
                data["— Commenting"] = "Not allowed"
        except:
            pass

        try:
            if get_json[0]['sex'] == 1:
                data["— Sex"] = 'Female'
            elif get_json[0]['sex'] == 2:
                data["— Sex"] = 'Male'
            else:
                data["— Sex"] = 'Not specified'
        except:
            pass

        try:
            if get_json[0]['verified'] == 1:
                data["— Verified"] = "Yes"
            else:
                data["— Verified"] = "No"
        except:
            pass

        try:
            data["— Birthday"] = get_json[0]['bdate']
        except:
            pass

        try:
            data["— Cropped avatar"] = get_json[0]['photo_max_orig']
        except:
            pass

        try:
            if len(get_json[0]["military"]) == 0:
                pass
            else:
                units = len(get_json[0]["military"]) - 1
                i = 0
                data['— Military'] = {}
                while i <= units:
                    try:
                        if get_json[0]["military"][i]['unit'] == get_json[0]["military"][i]['unit']:
                            data["— Military"]['#' + str(i + 1) + ', ' + get_json[0]["military"][i]['unit']] = {}
                    except:
                        pass

                    try:
                        if get_json[0]["military"][i]['from'] == get_json[0]["military"][i]['from']:
                            data["— Military"]['#' + str(i + 1) + ', ' + get_json[0]["military"][i]['unit']]['From'] = get_json[0]["military"][i]['from']
                    except:
                        pass

                    try:
                        if get_json[0]["military"][i]['from'] == get_json[0]["military"][i]['from']:
                            data["— Military"]['#' + str(i + 1) + ', ' + get_json[0]["military"][i]['unit']]['From'] = get_json[0]["military"][i]['from']
                    except:
                        pass

                    try:
                        if get_json[0]["military"][i]['until'] == get_json[0]["military"][i]['until']:
                            data["— Military"]['#' + str(i + 1) + ', ' + get_json[0]["military"][i]['unit']]['Until'] = get_json[0]["military"][i]['until']
                    except:
                        pass
                    i = i + 1
        except:
            pass

        try:
            if get_json[0]['relation'] == 0:
                pass
            else:
                data["— Relationship status"] = {}
                if get_json[0]['relation'] == 1:
                    data["— Relationship status"]["Relationship"] = "Single"
                elif get_json[0]['relation'] == 2:
                    data["— Relationship status"]["Relationship"] = "In a relationship"
                elif get_json[0]['relation'] == 3:
                    data["— Relationship status"]["Relationship"] = "Engaged"
                elif get_json[0]['relation'] == 4:
                    data["— Relationship status"]["Relationship"] = "Married"
                elif get_json[0]['relation'] == 5:
                    data["— Relationship status"]["Relationship"] = "Complicated"
                elif get_json[0]['relation'] == 6:
                    data["— Relationship status"]["Relationship"] = "Searching"
                elif get_json[0]['relation'] == 7:
                    data["— Relationship status"]["Relationship"] = "In love"
            try:
                data["— Relationship status"]["Partner ID"] = "vk.com/id" + str(get_json[0]['relation_partner']['id'])
            except:
                pass

            try:
                data["— Relationship status"]["First name"] = get_json[0]['relation_partner']["first_name"]
            except:
                pass

            try:
                data["— Relationship status"]["Last name"] = get_json[0]['relation_partner']["last_name"]
            except:
                pass
        except:
            pass

        try:
            if get_json[0]["relatives"] == get_json[0]["relatives"]:
                data["— Relatives"] = {}
                relatives = []
                for item in get_json[0]["relatives"]:
                    if item["id"] < 0:
                        relatives.append(item["type"].capitalize() + ":" + " no link :(")
                    else:
                        relatives.append(item["type"].capitalize() + ":" + " vk.com/id" + str(item['id']))
                data["— Relatives"] = relatives

            if len(data["— Relatives"]) == 0:
                del data["— Relatives"]
        except:
            pass

        try:
            if len(get_json[0]["schools"]) == 0:
                pass
            else:
                schools = len(get_json[0]["schools"]) - 1
                i = 0
                data['— Schools'] = {}
                while i <= schools:
                    try:
                        if get_json[0]['schools'][i]['name'] == get_json[0]['schools'][i]['name']:
                            data['— Schools']['#' + str(i + 1) + ', ' + get_json[0]['schools'][i]['name']] = {}
                        else:
                            pass
                    except:
                        pass

                    try:
                        if get_json[0]['schools'][i]['year_from'] == get_json[0]['schools'][i]['year_from']:
                            data['— Schools']['#' + str(i + 1) + ', ' + get_json[0]['schools'][i]['name']]['From'] = get_json[0]['schools'][i]['year_from']
                        else:
                            pass
                    except:
                        pass

                    try:
                        if get_json[0]['schools'][i]['year_to'] == get_json[0]['schools'][i]['year_to']:
                            data['— Schools']['#' + str(i + 1) + ', ' + get_json[0]['schools'][i]['name']]['To'] = get_json[0]['schools'][i]['year_to']
                        else:
                            pass
                    except:
                        pass

                    try:
                        if get_json[0]['schools'][i]['year_graduated'] == get_json[0]['schools'][i]['year_graduated']:
                            data['— Schools']['#' + str(i + 1) + ', ' + get_json[0]['schools'][i]['name']]['Graduated'] = get_json[0]['schools'][i]['year_graduated']
                        else:
                            pass
                    except:
                        pass

                    try:
                        if get_json[0]['schools'][i]['class'] == "":
                            pass
                        else:
                            data['— Schools']['#' + str(i + 1) + ', ' + get_json[0]['schools'][i]['name']]['Class'] = get_json[0]['schools'][i]['class']
                    except:
                        pass

                    try:
                        if get_json[0]['schools'][i]['speciality'] == get_json[0]['schools'][i]['speciality']:
                            data['— Schools']['#' + str(i + 1) + ', ' + get_json[0]['schools'][i]['name']]['Speciality'] = get_json[0]['schools'][i]['speciality']
                        else:
                            pass
                    except:
                        pass

                    try:
                        if get_json[0]['schools'][i]['type_str'] == get_json[0]['schools'][i]['type_str']:
                            data['— Schools']['#' + str(i + 1) + ', ' + get_json[0]['schools'][i]['name']]['Type'] = get_json[0]['schools'][i]['type_str']
                        else:
                            pass
                    except:
                        pass
                    i = i + 1
        except:
            pass

        try:
            if len(get_json[0]["career"]) == 0:
                pass
            else:
                jobs = len(get_json[0]["career"]) - 1
                i = 0
                data["— Career"] = {}
                while i <= jobs:
                    try:
                        try:
                            if get_json[0]["career"][i]['group_id'] == get_json[0]["career"][i]['group_id']:
                                data["— Career"]['#' + str(i + 1) + ', ' + 'vk.com/public' + str(get_json[0]["career"][i]['group_id'])] = {}
                        except:
                            pass

                        try:
                            if get_json[0]["career"][i]['company'] == get_json[0]["career"][i]['company']:
                                data["— Career"]['#' + str(i + 1) + ', ' + str(get_json[0]["career"][i]['company'])] = {}
                        except:
                            pass

                        try:
                            if get_json[0]["career"][i]['from'] == get_json[0]["career"][i]['from']:
                                data["— Career"]['#' + str(i + 1) + ', ' + 'vk.com/public' + str(get_json[0]["career"][i]['group_id'])]['From'] = get_json[0]["career"][i]['from']
                        except:
                            pass
                        try:
                            if get_json[0]["career"][i]['from'] == get_json[0]["career"][i]['from']:
                                data["— Career"]['#' + str(i + 1) + ', ' + str(get_json[0]["career"][i]['company'])]['From'] = get_json[0]["career"][i]['from']
                        except:
                            pass

                        try:
                            if get_json[0]["career"][i]['until'] == get_json[0]["career"][i]['until']:
                                data["— Career"]['#' + str(i + 1) + ', ' + 'vk.com/public' + str(get_json[0]["career"][i]['group_id'])]['To'] = get_json[0]["career"][i]['until']
                        except:
                            pass

                        try:
                            if get_json[0]["career"][i]['until'] == get_json[0]["career"][i]['until']:
                                data["— Career"]['#' + str(i + 1) + ', ' + str(get_json[0]["career"][i]['company'])]['To'] = get_json[0]["career"][i]['until']
                        except:
                            pass

                        try:
                            if get_json[0]["career"][i]['position'] == get_json[0]["career"][i]['position']:
                                data["— Career"]['#' + str(i + 1) + ', ' + 'vk.com/public' + str(get_json[0]["career"][i]['group_id'])]['Position'] = get_json[0]["career"][i]['position']
                        except:
                            pass

                        try:
                            if get_json[0]["career"][i]['position'] == get_json[0]["career"][i]['position']:
                                data["— Career"]['#' + str(i + 1) + ', ' + str(get_json[0]["career"][i]['company'])]['Position'] = get_json[0]["career"][i]['position']
                        except:
                            pass
                    except:
                        pass
                    i = i + 1
        except:
            pass

        try:
            if get_json[0]['site'] == "":
                pass
            else:
                data["— Website"] = get_json[0]["site"]
        except:
            pass

        try:
            if get_json[0]["last_seen"]["time"] == get_json[0]["last_seen"]["time"]:
                data["— Last seen"] = datetime.utcfromtimestamp(get_json[0]["last_seen"]["time"]).strftime('%Y-%m-%d %H:%M:%S')
            else:
                data["— Last seen"] = "Hidden"
        except:
            pass

        try:
            if get_json[0]["last_seen"]["platform"] == 1:
                data["— Platform"] = "Mobile (m.vk.com)"
            elif get_json[0]["last_seen"]["platform"] == 2:
                data["— Platform"] = "iPhone"
            elif get_json[0]["last_seen"]["platform"] == 3:
                data["— Platform"] = "iPad"
            elif get_json[0]["last_seen"]["platform"] == 4:
                data["— Platform"] = "Android"
            elif get_json[0]["last_seen"]["platform"] == 5:
                data["— Platform"] = "Windows Phone"
            elif get_json[0]["last_seen"]["platform"] == 6:
                data["— Platform"] = "Windows 8"
            elif get_json[0]["last_seen"]["platform"] == 7:
                data["— Platform"] = "Web"
            else:
                data["— Platform"] = "VK Me (vk.me/app)"
        except:
            pass

        try:
            if get_json[0]["status"] == "":
                pass
            else:
                data["— Status"] = get_json[0]["status"]
        except:
            pass

        try:
            if get_json[0]["occupation"]["name"] == get_json[0]["occupation"]["name"]:
                data['— Occupation'] = {}
                data['— Occupation']["Place"] = get_json[0]["occupation"]["name"]

            if get_json[0]["occupation"]["type"] == get_json[0]["occupation"]["type"]:
                data['— Occupation']["Type"] = get_json[0]["occupation"]["type"]
        except:
            pass

        try:
            data["— Domain"] = get_json[0]["screen_name"]
        except:
            pass

        try:
            if get_json[0]["activities"] == "":
                pass
            else:
                data["— Activities"] = get_json[0]["activities"]
        except:
            pass

        try:
            if get_json[0]["interests"] == "":
                pass
            else:
                data["— Interests"] = get_json[0]["interests"]
        except:
            pass

        try:
            if get_json[0]["music"] == "":
                pass
            else:
                data["— Music"] = get_json[0]["music"]
        except:
            pass

        try:
            if get_json[0]["movies"] == "":
                pass
            else:
                data["— Movies"] = get_json[0]["movies"]
        except:
            pass

        try:
            if get_json[0]["tv"] == "":
                pass
            else:
                data["— TV"] = get_json[0]["tv"]
        except:
            pass

        try:
            if get_json[0]["books"] == "":
                pass
            else:
                data["— Books"] = get_json[0]["books"]
        except:
            pass

        try:
            if get_json[0]["games"] == "":
                pass
            else:
                data["— Games"] = get_json[0]["games"]
        except:
            pass

        try:
            if get_json[0]["about"] == "":
                pass
            else:
                data["— About"] = get_json[0]["about"]
        except:
            pass

        try:
            if get_json[0]["quotes"] == "":
                pass
            else:
                data["— Quotes"] = get_json[0]["quotes"]
        except:
            pass

        try:
            if get_json[0]["counters"] == get_json[0]["counters"]:
                data["— Number of"] = {}
                try:
                    if get_json[0]["counters"]["albums"] == 0:
                        pass
                    else:
                        data["— Number of"]["Albums"] = get_json[0]["counters"]["albums"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["videos"] == 0:
                        pass
                    else:
                        data["— Number of"]["Videos"] = get_json[0]["counters"]["videos"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["audios"] == 0:
                        pass
                    else:
                        data["— Number of"]["Audios"] = get_json[0]["counters"]["audios"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["photos"] == 0:
                        pass
                    else:
                        data["— Number of"]["Photos"] = get_json[0]["counters"]["photos"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["notes"] == 0:
                        pass
                    else:
                        data["— Number of"]["Notes"] = get_json[0]["counters"]["notes"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["friends"] == 0:
                        pass
                    else:
                        data["— Number of"]["Friends"] = get_json[0]["counters"]["friends"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["groups"] == 0:
                        pass
                    else:
                        data["— Number of"]["Groups"] = get_json[0]["counters"]["groups"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["posts"] == 0:
                        pass
                    else:
                        data["— Number of"]["Posts"] = get_json[0]["counters"]["posts"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["gifts"] == 0:
                        pass
                    else:
                        data["— Number of"]["Gifts"] = get_json[0]["counters"]["gifts"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["user_videos"] == 0:
                        pass
                    else:
                        data["— Number of"]["User's tagged video"] = get_json[0]["counters"]["user_video"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["followers"] == 0:
                        pass
                    else:
                        data["— Number of"]["Followers"] = get_json[0]["counters"]["followers"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["user_photos"] == 0:
                        pass
                    else:
                        data["— Number of"]["User's tagged photos"] = get_json[0]["counters"]["user_photos"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["subscriptions"] == 0:
                        pass
                    else:
                        data["— Number of"]["Subscriptions"] = get_json[0]["counters"]["subscriptions"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["pages"] == 0:
                        pass
                    else:
                        data["— Number of"]["Pages"] = get_json[0]["counters"]["pages"]
                except:
                    pass
        except:
            pass

        try:
            if get_json[0]["personal"] == get_json[0]["personal"]:
                data["— Personal"] = {}
                try:
                    if get_json[0]["personal"]["political"] == get_json[0]["personal"]["political"]:
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
                except:
                    pass

                try:
                    langs = ', '.join(map(str, get_json[0]["personal"]["langs"]))
                    data["— Personal"]["Languages"] = langs
                except:
                    pass

                try:
                    data["— Personal"]["Religion"] = get_json[0]["personal"]["religion"]
                except:
                    pass

                try:
                    data["— Personal"]["Inspired by"] = get_json[0]["personal"]["inspired_by"]
                except:
                    pass

                try:
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
                except:
                    pass

                try:
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
                except:
                    pass

                try:
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
                except:
                    pass

                try:
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
                except:
                    pass

            if len(data["— Personal"]) == 0:
                del data["— Personal"]

        except:
            pass

        try:
            if len(get_json[0]["mobile_phone"]) == 0:
                pass
            else:
                data["— Mobile"] = get_json[0]["mobile_phone"]
        except:
            pass

        try:
            if len(get_json[0]["home_phone"]) == 0:
                pass
            else:
                data["— Home phone"] = get_json[0]["home_phone"]
        except:
            pass

        try:
            data["— Skype"] = get_json[0]["skype"]
        except:
            pass

        try:
            data["— Instagram"] = "instagram.com/" + get_json[0]["instagram"]
        except:
            pass

        try:
            data["— Twitter"] = "twitter.com/" + get_json[0]["twitter"]
        except:
            pass

        try:
            data["— LiveJournal"] = get_json[0]["livejournal"] + ".livejournal.com"
        except:
            pass

        try:
            data["— Facebook"] = "facebook.com/profile.php?id=" + get_json[0]["facebook"]
        except:
            pass

        try:
            data["— Country"] = get_json[0]["country"]["title"]
        except:
            pass

        try:
            data["— City"] = get_json[0]["city"]["title"]
        except:
            pass

        try:
            if get_json[0]["home_town"] == "":
                pass
            else:
                data["— Hometown"] = get_json[0]["home_town"]
        except:
            pass

        try:
            link = settings.FOAF_LINK + str(get_json[0]['id'])
            with urllib.request.urlopen(link) as response:
                vk_xml = response.read().decode("windows-1251")
            parsed_xml = str(re.findall(r'ya:created dc:date="(.*)"', vk_xml))
            if len(parsed_xml) == 0:
                pass
            else:
                reg_date = str(datetime.strptime(parsed_xml, "['%Y-%m-%dT%H:%M:%S%z']"))
                data["— Registered"] = reg_date[:19]
        except:
            pass

        try:
            full_size_ava = max(get_json[0]["crop_photo"]["photo"]['sizes'],
                                key=lambda line: int(line['width']))
            data["— Full-size avatar"] = full_size_ava['url']
        except:
            pass

        try:
            data["— Date of avatar"] = datetime.utcfromtimestamp(
                get_json[0]["crop_photo"]["photo"]["date"]).strftime(
                '%Y-%m-%d %H:%M:%S')
        except:
            pass

        try:
            if len(get_json[0]["universities"]) == 0:
                pass
            else:
                unis = len(get_json[0]["universities"]) - 1
                i = 0
                data["— Education"] = {}
                while i <= unis:
                    try:
                        if get_json[0]["universities"][i]['name'] == get_json[0]["universities"][i]['name']:
                            data["— Education"]['#' + str(i + 1) + ', ' + str(get_json[0]["universities"][i]['name'])] = {}
                    except:
                        pass

                    try:
                        if get_json[0]["universities"][i]['faculty_name'] == get_json[0]["universities"][i]['faculty_name']:
                            data["— Education"]['#' + str(i + 1) + ', ' + str(get_json[0]["universities"][i]['name'])]["Faculty"] = {}
                            data["— Education"]['#' + str(i + 1) + ', ' + str(get_json[0]["universities"][i]['name'])]["Faculty"] = get_json[0]["universities"][i]['faculty_name']
                    except:
                        pass

                    try:
                        if get_json[0]["universities"][i]['chair_name'] == get_json[0]["universities"][i]['chair_name']:
                            data["— Education"]['#' + str(i + 1) + ', ' + str(get_json[0]["universities"][i]['name'])]["Study program"] = {}
                            data["— Education"]['#' + str(i + 1) + ', ' + str(get_json[0]["universities"][i]['name'])]["Study program"] = get_json[0]["universities"][i]['chair_name']
                    except:
                        pass

                    try:
                        if get_json[0]["universities"][i]['graduation'] == get_json[0]["universities"][i]['graduation']:
                            data["— Education"]['#' + str(i + 1) + ', ' + str(get_json[0]["universities"][i]['name'])]["Graduation"] = {}
                            data["— Education"]['#' + str(i + 1) + ', ' + str(get_json[0]["universities"][i]['name'])]["Graduation"] = get_json[0]["universities"][i]['graduation']
                    except:
                        pass

                    try:
                        if get_json[0]["universities"][i]['education_form'] == get_json[0]["universities"][i]['education_form']:
                            data["— Education"]['#' + str(i + 1) + ', ' + str(get_json[0]["universities"][i]['name'])]["Graduation form"] = {}
                            data["— Education"]['#' + str(i + 1) + ', ' + str(get_json[0]["universities"][i]['name'])]["Graduation form"] = get_json[0]["universities"][i]['education_form']
                    except:
                        pass

                    try:
                        if get_json[0]["universities"][i]['education_status'] == get_json[0]["universities"][i]['education_status']:
                            data["— Education"]['#' + str(i + 1) + ', ' + str(get_json[0]["universities"][i]['name'])]["Education status"] = {}
                            data["— Education"]['#' + str(i + 1) + ', ' + str(get_json[0]["universities"][i]['name'])]["Education status"] = get_json[0]["universities"][i]['education_status']
                    except:
                        pass
                    i = i + 1
        except:
            pass

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

        bot.send_message(message.from_user.id,
                         "⌛ Requested info for " + at_text.lower() + " on " + str(
                             datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")) + " UTC")

        for text in ready_text:
            bot.send_message(message.from_user.id, text)

    except:
        bot.send_message(message.from_user.id, "<b>⚠️ Something went wrong ;( This could be why:</b>\n"
                                               "1. Wrong user ID\n"
                                               "2. ID contains non Latin characters\n"
                                               "3. ID contains special characters (e.g. comma, tilde)\n",
                         parse_mode="HTML")


while True:
    try:
        bot.polling(none_stop=True)
    except Exception:
        time.sleep(15)
