#! /usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import requests
import settings
import time
import urllib.request
import re
import traceback
from telebot import util
from datetime import datetime

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


def find_at(msg):
    for text in msg:
        if text in text:
            return text


def get_country_str(country):
    time.sleep(0.35)
    country_str = requests.get("https://api.vk.com/method/database.getCountriesById?country_ids=" + str(country) +
                               "&access_token=" + settings.VK_TOKEN + "&v=5.124").json()['response'][0]
    return country_str


def get_city_str(city):
    time.sleep(0.35)
    city_str = requests.get("https://api.vk.com/method/database.getCitiesById?city_ids=" + str(city) +
                            "&access_token=" + settings.VK_TOKEN + "&v=5.124").json()['response'][0]
    return city_str


@bot.message_handler(commands=['start'])
def regular_message(message):
    bot.send_message(message.from_user.id, "<b>Welcome to bot! 🤖</b>\n"
                                           "\nPlease send the page user ID 🔎"
                                           '\n(eg. "<b>durov</b>" or "<b>id1</b>")', parse_mode="HTML")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.from_user.id, "Bot collects all main information (if available) from user page."
                                           "To start, send a text message with ID to get info about the user.\n"
                                           "\n<b>DISCLAIMER: All data is taken from public sources by VK API's "
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
        request = requests.get("https://api.vk.com/method/users.get?user_ids=" + at_text + "&fields=" +
                         settings.FIELDS + "&access_token=" + settings.VK_TOKEN + "&v=5.124").json()['response'][0]

        data = {}

        if 'id' in request:
            data["— ID"] = request['id']

        if 'first_name' and 'last_name' in request:
            data["— Name"] = request['first_name'] + ' ' + request['last_name']
        else:
            if 'first_name' in request:
                if request['first_name'] == "":
                    pass
                else:
                    data["— First name"] = request['first_name']

            if 'last_name' in request:
                if request['last_name'] == "":
                    pass
                else:
                    data["— Last name"] = request['last_name']

        if 'nickname' in request:
            if request['nickname'] == "":
                pass
            else:
                data["— Middle name"] = request['nickname']

        if 'maiden_name' in request:
            if request['maiden_name'] == "":
                pass
            else:
                data["— Maiden name"] = request['maiden_name']

        if 'deactivated' in request:
            if request['deactivated'] == "deleted":
                data["— Page status"] = "Deleted"
            else:
                data["— Page status"] = "Blocked"

        if 'can_write_private_message' in request:
            if 'deactivated' in request:
                pass
            else:
                if request["can_write_private_message"] == 0:
                    data["— PM"] = "Not allowed"
                else:
                    data["— PM"] = "Allowed"

        if 'is_closed' in request:
            if not request['is_closed']:
                data["— Page privacy"] = "Open"
                if 'can_see_all_posts' in request:
                    if request["can_see_all_posts"] == 0:
                        data["— All posts"] = "Hidden"
                    else:
                        data["— All posts"] = "Visible"

                if 'can_post' in request:
                    if 'deactivated' in request:
                        pass
                    else:
                        if request["can_post"] == 0:
                            data["— Posting"] = "Not allowed"
                        else:
                            data["— Posting"] = "Allowed"

                if 'can_see_audio' in request:
                    if request["can_see_audio"] == 0:
                        data["— Audio"] = "Hidden"
                    else:
                        data["— Audio"] = "Visible"

                if 'wall_comments' in request:
                    if request['wall_comments'] == 1:
                        data["— Commenting"] = "Allowed"
                    else:
                        data["— Commenting"] = "Not allowed"
            else:
                data["— Page privacy"] = "Closed"

        if 'can_send_friend_request' in request:
            if request["can_send_friend_request"] == 0:
                data["— Friend request"] = "Not allowed"
            else:
                data["— Friend request"] = "Allowed"

        if 'sex' in request:
            if 'first_name' in request:
                if request['first_name'] == "DELETED":
                    pass
                else:
                    if request['sex'] == 1:
                        data["— Sex"] = 'Female'
                    if request['sex'] == 2:
                        data["— Sex"] = 'Male'

        if 'verified' in request:
            if request['verified'] == 1:
                data["— Verified"] = "Yes"

        if 'bdate' in request:
            data["— Birthday"] = request['bdate']

        if 'military' in request:
            if len(request["military"]) == 0:
                pass
            else:
                data['— Military'] = {}
                x = 0
                for i in request["military"]:
                    if 'unit' in i:
                        data["— Military"]["#" + str(x + 1) + ", " + i['unit']] = {}
                    if 'country_id' in i:
                        data["— Military"]["#" + str(x + 1) + ", " + i['unit']]['Country'] = \
                            get_country_str(i['country_id'])['title']
                    if 'from' and 'until' in i:
                        data["— Military"]["#" + str(x + 1) + ", " + i['unit']]['Time'] = str(i['from']) + ' — ' + str(
                            i['until'])
                    else:
                        if 'from' in i:
                            data["— Military"]["#" + str(x + 1) + ", " + i['unit']]['From'] = i['from']
                        if 'until' in i:
                            data["— Military"]["#" + str(x + 1) + ", " + i['unit']]['Until'] = i['until']
                    x += 1

        if 'relation' in request:
            if request['relation'] == 0:
                pass
            else:
                data["— Relationship"] = {}
                if request['relation'] == 1:
                    data["— Relationship"]["Status"] = "Single"
                elif request['relation'] == 2:
                    data["— Relationship"]["Status"] = "In a relationship"
                elif request['relation'] == 3:
                    data["— Relationship"]["Status"] = "Engaged"
                elif request['relation'] == 4:
                    data["— Relationship"]["Status"] = "Married"
                elif request['relation'] == 5:
                    data["— Relationship"]["Status"] = "Complicated"
                elif request['relation'] == 6:
                    data["— Relationship"]["Status"] = "Searching"
                elif request['relation'] == 7:
                    data["— Relationship"]["Status"] = "In love"
                elif request['relation'] == 8:
                    data["— Relationship"]["Status"] = "In a civil union"

            if 'relation_partner' in request:
                data["— Relationship"]["ID"] = "@id" + str(request['relation_partner']['id'])
                if 'first_name' and 'last_name' in request['relation_partner']:
                    data["— Relationship"]["Name"] = request['relation_partner']["first_name"] + ' ' + \
                                                     request['relation_partner']["last_name"]
                else:
                    if 'first_name' in request['relation_partner']:
                        data["— Relationship"]["First name"] = request['relation_partner']["first_name"]
                    if 'last_name' in request['relation_partner']:
                        data["— Relationship"]["Last name"] = request['relation_partner']["last_name"]

        if 'relatives' in request:
            if len(request["relatives"]) == 0:
                pass
            else:
                data["— Relatives"] = {}
                relatives = []
                for i in request["relatives"]:
                    if i["id"] < 0:
                        if 'id' and 'name' in i:
                            relatives.append(i["type"].capitalize() + ": " + i['name'])
                        else:
                            relatives.append(i["type"].capitalize() + ":" + " no link")
                    else:
                        relatives.append(i["type"].capitalize() + ":" + " @id" + str(i['id']))
                data["— Relatives"] = relatives

        if 'schools' in request:
            if len(request["schools"]) == 0:
                pass
            else:
                data['— Schools'] = {}
                x = 0
                for i in request["schools"]:
                    if 'name' in i:
                        data['— Schools']["#" + str(x + 1) + ", " + i['name']] = {}

                    if 'country' and 'city' in i:
                        country_str = get_country_str(i['country'])['title']
                        city_str = get_city_str(i['city'])['title']
                        data['— Schools']["#" + str(x + 1) + ", " + i['name']]['Place'] = str(country_str) + ', ' + str(
                            city_str)
                    else:
                        if 'country' in i:
                            data['— Schools']["#" + str(x + 1) + ", " + i['name']]['Country'] = \
                                get_country_str(i['country'])['title']
                        if 'city' in i:
                            data['— Schools']["#" + str(x + 1) + ", " + i['name']]['City'] = get_city_str(i['city'])[
                                'title']

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
                    # if 'type_str' in i:
                    #     data['— Schools']["#" + str(x + 1) + ", " + i['name']]['Type'] = i['type_str']
                    x += 1

        if 'career' in request:
            if len(request["career"]) == 0:
                pass
            else:
                data["— Career"] = {}
                x = 0
                for i in request["career"]:
                    if 'group_id' in i:
                        data["— Career"]["#" + str(x + 1) + ", " + '@public' + str(i['group_id'])] = {}
                        if 'country_id' and 'city_id' in i:
                            country_str = get_country_str(i['country_id'])['title']
                            city_str = get_city_str(i['city_id'])['title']
                            data["— Career"]["#" + str(x + 1) + ", " + '@public' + str(i['group_id'])][
                                'Place'] = str(country_str) + ', ' + str(city_str)
                        else:
                            if 'country_id' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + '@public' + str(i['group_id'])][
                                    'Country'] = get_country_str(i['country_id'])['title']
                            if 'city_id' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + '@public' + str(i['group_id'])][
                                    'City'] = get_city_str(i['city_id'])['title']

                        if 'from' and 'until' in i:
                            data["— Career"]["#" + str(x + 1) + ", " + '@public' + str(i['group_id'])][
                                'Period'] = str(i['from']) + ' — ' + str(i['until'])
                        else:
                            if 'from' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + '@public' + str(i['group_id'])][
                                    'From'] = i['from']
                            if 'until' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + '@public' + str(i['group_id'])]['To'] = \
                                    i['until']
                        if 'position' in i:
                            data["— Career"]["#" + str(x + 1) + ", " + '@public' + str(i['group_id'])][
                                'Position'] = i['position']

                    if 'company' in i:
                        data["— Career"]["#" + str(x + 1) + ", " + i['company']] = {}

                        if 'country_id' and 'city_id' in i:
                            country_str = get_country_str(i['country_id'])['title']
                            city_str = get_city_str(i['city_id'])['title']
                            data["— Career"]["#" + str(x + 1) + ", " + i['company']]['Place'] = str(
                                country_str) + ', ' + str(city_str)
                        else:
                            if 'country_id' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + i['company']]['Country'] = \
                                    get_country_str(i['country_id'])['title']
                            if 'city_id' in i:
                                data["— Career"]["#" + str(x + 1) + ", " + i['company']]['City'] = \
                                    get_city_str(i['city_id'])['title']

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

        if 'site' in request:
            if request['site'] == "":
                pass
            else:
                data["— Site"] = request["site"]

        if 'last_seen' in request:
            if 'time' in request["last_seen"]:
                data["— Last seen"] = datetime.utcfromtimestamp(request["last_seen"]["time"]).strftime(
                    '%Y-%m-%d %H:%M:%S')
            if 'platform' in request["last_seen"]:
                if request["last_seen"]["platform"] == 1:
                    data["— Platform"] = "m.vk.com"
                if request["last_seen"]["platform"] == 2:
                    data["— Platform"] = "iPhone"
                if request["last_seen"]["platform"] == 3:
                    data["— Platform"] = "iPad"
                if request["last_seen"]["platform"] == 4:
                    data["— Platform"] = "Android"
                if request["last_seen"]["platform"] == 5:
                    data["— Platform"] = "Windows Phone"
                if request["last_seen"]["platform"] == 6:
                    data["— Platform"] = "Windows 8"
                if request["last_seen"]["platform"] == 7:
                    data["— Platform"] = "vk.com"
        else:
            if "deactivated" in request:
                pass
            else:
                # data["— Platform"] = "vk.me/app"
                data["— Last seen"] = "Hidden by vk.me/app"

        if 'status' in request:
            if request["status"] == "":
                pass
            else:
                data["— Status"] = request["status"]

        if 'occupation' in request:
            data['— Occupation'] = {}
            if 'name' and 'id' in request["occupation"]:
                data['— Occupation']["Place"] = request["occupation"]["name"]
                data['— Occupation']['ID'] = '@public' + str(request["occupation"]["id"])
            else:
                data['— Occupation']["Place"] = request["occupation"]["name"]
            # if 'type' in request["occupation"]:
            #     data['— Occupation']["Type"] = request["occupation"]["type"]

        if 'screen_name' in request:
            data["— Domain"] = request["screen_name"]

        if 'activities' in request:
            if request["activities"] == "":
                pass
            else:
                data["— Activities"] = request["activities"]

        if 'interests' in request:
            if request["interests"] == "":
                pass
            else:
                data["— Interests"] = request["interests"]

        if 'music' in request:
            if request["music"] == "":
                pass
            else:
                data["— Music"] = request["music"]

        if 'movies' in request:
            if request["movies"] == "":
                pass
            else:
                data["— Movies"] = request["movies"]

        if 'tv' in request:
            if request["tv"] == "":
                pass
            else:
                data["— TV"] = request["tv"]

        if 'books' in request:
            if request["books"] == "":
                pass
            else:
                data["— Books"] = request["books"]

        if 'games' in request:
            if request["games"] == "":
                pass
            else:
                data["— Games"] = request["games"]

        if 'about' in request:
            if request["about"] == "":
                pass
            else:
                data["— About"] = request["about"]

        if 'quotes' in request:
            if request["quotes"] == "":
                pass
            else:
                data["— Quotes"] = request["quotes"]

        if 'counters' in request:
            if len(request["counters"]) == 0:
                pass
            else:
                data["— Counters"] = {}

                if 'albums' in request["counters"]:
                    if request["counters"]["albums"] == 0:
                        pass
                    else:
                        data["— Counters"]["Albums"] = request["counters"]["albums"]

                if 'videos' in request["counters"]:
                    if request["counters"]["videos"] == 0:
                        pass
                    else:
                        data["— Counters"]["Videos"] = request["counters"]["videos"]

                if 'audios' in request["counters"]:
                    if request["counters"]["audios"] == 0:
                        pass
                    else:
                        data["— Counters"]["Audios"] = request["counters"]["audios"]

                if 'photos' in request["counters"]:
                    if request["counters"]["photos"] == 0:
                        pass
                    else:
                        data["— Counters"]["Photos"] = request["counters"]["photos"]

                if 'notes' in request["counters"]:
                    if request["counters"]["notes"] == 0:
                        pass
                    else:
                        data["— Counters"]["Notes"] = request["counters"]["notes"]

                if 'friends' in request["counters"]:
                    if request["counters"]["friends"] == 0:
                        pass
                    else:
                        data["— Counters"]["Friends"] = request["counters"]["friends"]

                if 'groups' in request["counters"]:
                    if request["counters"]["groups"] == 0:
                        pass
                    else:
                        data["— Counters"]["Groups"] = request["counters"]["groups"]

                if 'posts' in request["counters"]:
                    if request["counters"]["posts"] == 0:
                        pass
                    else:
                        data["— Counters"]["Posts"] = request["counters"]["posts"]

                if 'gifts' in request["counters"]:
                    if request["counters"]["gifts"] == 0:
                        pass
                    else:
                        data["— Counters"]["Gifts"] = request["counters"]["gifts"]

                if 'user_videos' in request["counters"]:
                    if request["counters"]["user_videos"] == 0:
                        pass
                    else:
                        data["— Counters"]["Tagged on videos"] = request["counters"]["user_video"]

                if 'followers' in request["counters"]:
                    if request["counters"]["followers"] == 0:
                        pass
                    else:
                        data["— Counters"]["Followers"] = request["counters"]["followers"]

                if 'user_photos' in request["counters"]:
                    if request["counters"]["user_photos"] == 0:
                        pass
                    else:
                        data["— Counters"]["Tagged on photos"] = request["counters"]["user_photos"]

                if 'subscriptions' in request["counters"]:
                    if request["counters"]["subscriptions"] == 0:
                        pass
                    else:
                        data["— Counters"]["Subscriptions"] = request["counters"]["subscriptions"]

                if 'pages' in request["counters"]:
                    if request["counters"]["pages"] == 0:
                        pass
                    else:
                        data["— Counters"]["Pages"] = request["counters"]["pages"]

        if 'personal' in request:
            if len(request['personal']) == 0:
                pass
            else:
                data["— Personal"] = {}
                if 'political' in request["personal"]:
                    if request["personal"]["political"] == 1:
                        data["— Personal"]["Political"] = "Communist"
                    elif request["personal"]["political"] == 2:
                        data["— Personal"]["Political"] = "Socialist"
                    elif request["personal"]["political"] == 3:
                        data["— Personal"]["Political"] = "Moderate"
                    elif request["personal"]["political"] == 4:
                        data["— Personal"]["Political"] = "Liberal"
                    elif request["personal"]["political"] == 5:
                        data["— Personal"]["Political"] = "Conservative"
                    elif request["personal"]["political"] == 6:
                        data["— Personal"]["Political"] = "Monarchist"
                    elif request["personal"]["political"] == 7:
                        data["— Personal"]["Political"] = "Ultraconservative"
                    elif request["personal"]["political"] == 8:
                        data["— Personal"]["Political"] = "Apathetic"
                    elif request["personal"]["political"] == 9:
                        data["— Personal"]["Political"] = "Libertarian"

                if 'langs' in request["personal"]:
                    langs = ', '.join(map(str, request["personal"]["langs"]))
                    data["— Personal"]["Languages"] = langs

                if 'religion' in request["personal"]:
                    data["— Personal"]["Religion"] = request["personal"]["religion"]

                if 'inspired_by' in request["personal"]:
                    data["— Personal"]["Inspired by"] = request["personal"]["inspired_by"]

                if 'people_main' in request["personal"]:
                    if request["personal"]["people_main"] == 1:
                        data["— Personal"]["People main"] = "Intellect & creativity"
                    elif request["personal"]["people_main"] == 2:
                        data["— Personal"]["People main"] = "Kindness & honesty"
                    elif request["personal"]["people_main"] == 3:
                        data["— Personal"]["People main"] = "Health & beauty"
                    elif request["personal"]["people_main"] == 4:
                        data["— Personal"]["People main"] = "Wealth & power"
                    elif request["personal"]["people_main"] == 5:
                        data["— Personal"]["People main"] = "Courage & persistance"
                    elif request["personal"]["people_main"] == 6:
                        data["— Personal"]["People main"] = "Humor & love for life"

                if 'life_main' in request["personal"]:
                    if request["personal"]["life_main"] == 1:
                        data["— Personal"]["Life main"] = "Family & children"
                    elif request["personal"]["life_main"] == 2:
                        data["— Personal"]["Life main"] = "Career & money"
                    elif request["personal"]["life_main"] == 3:
                        data["— Personal"]["Life main"] = "Entertainment & leisure"
                    elif request["personal"]["life_main"] == 4:
                        data["— Personal"]["Life main"] = "Science & research"
                    elif request["personal"]["life_main"] == 5:
                        data["— Personal"]["Life main"] = "Improving the world"
                    elif request["personal"]["life_main"] == 6:
                        data["— Personal"]["Life main"] = "Personal development"
                    elif request["personal"]["life_main"] == 7:
                        data["— Personal"]["Life main"] = "Beauty & art"
                    elif request["personal"]["life_main"] == 8:
                        data["— Personal"]["Life main"] = "Fame & influence"

                if 'smoking' in request["personal"]:
                    if request["personal"]["smoking"] == 1:
                        data["— Personal"]["Smoking"] = "Very negative"
                    elif request["personal"]["smoking"] == 2:
                        data["— Personal"]["Smoking"] = "Negative"
                    elif request["personal"]["smoking"] == 3:
                        data["— Personal"]["Smoking"] = "Neutral"
                    elif request["personal"]["smoking"] == 4:
                        data["— Personal"]["Smoking"] = "Compromisable"
                    elif request["personal"]["smoking"] == 5:
                        data["— Personal"]["Smoking"] = "Positive"

                if 'alcohol' in request["personal"]:
                    if request["personal"]["alcohol"] == 1:
                        data["— Personal"]["Alcohol"] = "Very negative"
                    elif request["personal"]["alcohol"] == 2:
                        data["— Personal"]["Alcohol"] = "Negative"
                    elif request["personal"]["alcohol"] == 3:
                        data["— Personal"]["Alcohol"] = "Neutral"
                    elif request["personal"]["alcohol"] == 4:
                        data["— Personal"]["Alcohol"] = "Compromisable"
                    elif request["personal"]["alcohol"] == 5:
                        data["— Personal"]["Alcohol"] = "Positive"

        if 'mobile_phone' in request:
            if len(request["mobile_phone"]) == 0:
                pass
            else:
                data["— Mobile"] = request["mobile_phone"]

        if 'home_phone' in request:
            if len(request["home_phone"]) == 0:
                pass
            else:
                data["— Home phone"] = request["home_phone"]

        if 'skype' in request:
            data["— Skype"] = request["skype"]

        if 'instagram' in request:
            data["— Instagram"] = "@" + request["instagram"]

        if 'twitter' in request:
            data["— Twitter"] = "@" + request["twitter"]

        if 'livejournal' in request:
            data["— LiveJournal"] = "@" + request["livejournal"]

        if 'facebook' in request:
            data["— Facebook"] = "facebook.com/profile.php?id=" + request["facebook"]

        if 'country' and 'city' in request:
            if 'title' in request["country"] and 'title' in request["city"]:
                data["— Location"] = request["country"]["title"] + ', ' + request["city"]["title"]
        else:
            if 'country' in request:
                if 'title' in request["country"]:
                    data["— Country"] = request["country"]["title"]

            if 'city' in request:
                if 'title' in request["city"]:
                    data["— City"] = request["city"]["title"]

        if 'home_town' in request:
            if request["home_town"] == "":
                pass
            else:
                data["— Hometown"] = request["home_town"]

        if 'deactivated' not in request:
            link = settings.FOAF_LINK + str(request['id'])
            with urllib.request.urlopen(link) as response:
                parsed_xml = str(re.findall(r'ya:created dc:date="(.*)"', response.read().decode("windows-1251")))
                data["— Registered"] = parsed_xml[2:-8].replace('T', " ")

        if 'has_photo' in request:
            if request['has_photo'] == 0:
                pass
            else:
                if 'crop_photo' not in request:
                    data["— Avatar"] = request["photo_max_orig"]
                else:
                    if 'crop_photo' in request:
                        if 'photo' in request["crop_photo"]:
                            full_size_ava = max(request["crop_photo"]["photo"]['sizes'],
                                                key=lambda line: int(line['width']))
                            data["— Avatar"] = full_size_ava['url']
                        if 'date' in request["crop_photo"]["photo"]:
                            data["— Avatar date"] = datetime.utcfromtimestamp(
                                request["crop_photo"]["photo"]["date"]).strftime('%Y-%m-%d %H:%M:%S')

        if 'universities' in request:
            if len(request["universities"]) == 0:
                pass
            else:
                data["— Education"] = {}
                x = 0
                for i in request["universities"]:
                    if 'name' in i:
                        data["— Education"]["#" + str(x + 1) + ", " + i['name']] = {}
                    if 'country' and 'city' in i:
                        if i['country'] == 0 and i['city'] == 0:
                            pass
                        else:
                            country_str = get_country_str(i['country'])['title']
                            city_str = get_city_str(i['city'])['title']
                            data["— Education"]["#" + str(x + 1) + ", " + i['name']][
                                "Place"] = country_str + ', ' + city_str
                    else:
                        if 'country' in i:
                            if i['country'] == 0:
                                pass
                            else:
                                data["— Education"]["#" + str(x + 1) + ", " + i['name']]["Country"] = \
                                    get_country_str(i['country'])['title']
                        if 'city' in i:
                            if i['city'] == 0:
                                pass
                            else:
                                data["— Education"]["#" + str(x + 1) + ", " + i['name']]["City"] = \
                                    get_city_str(i['city'])['title']

                    if 'faculty_name' in i:
                        data["— Education"]["#" + str(x + 1) + ", " + i['name']]["Faculty"] = i['faculty_name']
                    if 'chair_name' in i:
                        data["— Education"]["#" + str(x + 1) + ", " + i['name']]["Program"] = i['chair_name']
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
