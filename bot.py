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
            fields='photo_id, verified, sex, bdate, city, country, home_town, has_photo,'
                   'photo_max_orig, online, domain, has_mobile,'
                   'contacts, site, education, universities, schools, status, last_seen, followers_count,'
                   'occupation, nickname, relatives, relation, personal, connections, exports, activities, interests, '
                   'music, movies, tv, books, games, about, quotes, can_post, can_see_all_posts, can_see_audio,'
                   'can_write_private_message, can_send_friend_request, is_favorite, is_hidden_from_feed, timezone,'
                   'screen_name, maiden_name, crop_photo, career, military,'
                   'can_be_invited_group, counters',
            user_ids=at_text.lower())

        '''parsing reg date'''
        link = settings.FOAF_LINK + str(get_json[0]['id'])
        with urllib.request.urlopen(link) as response:
            vk_xml = response.read().decode("windows-1251")

        parsed_xml = re.findall(r'ya:created dc:date="(.*)"', vk_xml)
        get_json[0].update({"reg_date": parsed_xml})
        ''' parsing reg date'''

        dict = {}

        try:
            if get_json[0]['id'] == get_json[0]['id']:
                dict["ID"] = get_json[0]['id']
        except:
            pass

        try:
            if get_json[0]['first_name'] == "":
                pass
            else:
                dict["First name"] = get_json[0]['first_name']
        except:
            pass

        try:
            if get_json[0]['last_name'] == "":
                pass
            else:
                dict["Last name"] = get_json[0]['last_name']
        except:
            pass

        try:
            if get_json[0]['deactivated'] == get_json[0]['deactivated']:
                if get_json[0]['deactivated'] == "deleted":
                    dict["Page status"] = "Deleted"
                else:
                    dict["Page status"] = "Blocked"
        except:
            pass

        try:
            if get_json[0]["can_write_private_message"] == get_json[0]["can_write_private_message"]:
                if get_json[0]["can_write_private_message"] == 0:
                    dict["PM"] = "Not allowed"
                else:
                    dict["PM"] = "Allowed"
        except:
            pass

        try:
            if get_json[0]["can_see_all_posts"] == get_json[0]["can_see_all_posts"]:
                if get_json[0]["can_see_all_posts"] == 0:
                    dict["See all posts"] = "Not allowed"
                else:
                    dict["See all posts"] = "Allowed"
        except:
            pass

        try:
            if get_json[0]["can_post"] == get_json[0]["can_post"]:
                if get_json[0]["can_post"] == 0:
                    dict["Posting"] = "Not allowed"
                else:
                    dict["Posting"] = "Allowed"
        except:
            pass

        try:
            if get_json[0]["can_see_audio"] == get_json[0]["can_see_audio"]:
                if get_json[0]["can_see_audio"] == 0:
                    dict["Audio"] = "Not allowed"
                else:
                    dict["Audio"] = "Allowed"
        except:
            pass

        try:
            if get_json[0]['sex'] == get_json[0]['sex']:
                if get_json[0]['sex'] == 1:
                    dict["Sex"] = 'Female'
                if get_json[0]['sex'] == 2:
                    dict["Sex"] = 'Male'
                else:
                    dict["Sex"] = 'Not specified'
        except:
            pass

        try:
            if get_json[0]['verified'] == get_json[0]['verified']:
                if get_json[0]['verified'] == 1:
                    dict["Verified"] = "Yes"
                else:
                    dict["Verified"] = "No"
        except:
            pass

        try:
            if get_json[0]['bdate'] == get_json[0]['bdate']:
                dict["Birth date"] = get_json[0]['bdate']
        except:
            pass

        try:
            if get_json[0]['photo_max_orig'] == get_json[0]['photo_max_orig']:
                dict["Cropped avatar"] = get_json[0]['photo_max_orig']
        except:
            pass

        try:
            if get_json[0]['relation'] == get_json[0]['relation']:
                dict["Relationship"] = {}
                if get_json[0]['relation'] == 1:
                    dict["Relationship"]["Relationship"] = "Single"
                if get_json[0]['relation'] == 2:
                    dict["Relationship"]["Relationship"] = "In a relationship"
                if get_json[0]['relation'] == 3:
                    dict["Relationship"]["Relationship"] = "Engaged"
                if get_json[0]['relation'] == 4:
                    dict["Relationship"]["Relationship"] = "Married"
                if get_json[0]['relation'] == 5:
                    dict["Relationship"]["Relationship"] = "Complicated"
                if get_json[0]['relation'] == 6:
                    dict["Relationship"]["Relationship"] = "Searching"
                if get_json[0]['relation'] == 7:
                    dict["Relationship"]["Relationship"] = "In love"

            if get_json[0]['relation_partner'] == get_json[0]['relation_partner']:
                dict["Relationship"]["Partner ID"] = "vk.com/id" + str(get_json[0]['relation_partner']['id'])

            if get_json[0]['relation_partner']["first_name"] == get_json[0]['relation_partner']["first_name"]:
                dict["Relationship"]["Fisrt name"] = get_json[0]['relation_partner']["first_name"]

            if get_json[0]['relation_partner']["last_name"] == get_json[0]['relation_partner']["last_name"]:
                dict["Relationship"]["Last name"] = get_json[0]['relation_partner']["last_name"]

            if len(dict["Relationship"]) == 0:
                del dict["Relationship"]
        except:
            pass

        try:
            if get_json[0]["relatives"] == get_json[0]["relatives"]:
                dict["Relatives"] = {}
                relatives = []
                for item in get_json[0]["relatives"]:
                    if item["id"] < 0:
                        relatives.append(item["type"].capitalize() + ":" + " no link :(")
                    else:
                        relatives.append(item["type"].capitalize() + ":" + " vk.com/id" + str(item['id']))
                dict["Relatives"] = relatives

            if len(dict["Relatives"]) == 0:
                del dict["Relatives"]
        except:
            pass

        try:
            if get_json[0]["schools"] == get_json[0]["schools"]:
                dict["Schools"] = {}
                schools = []
                for item in get_json[0]["schools"]:
                    schools.append((item["name"]))
                dict["Schools"] = schools

            if len(dict["Schools"]) == 0:
                del dict["Schools"]
        except:
            pass

        try:
            if get_json[0]['site'] == "":
                pass
            else:
                dict["Site"] = get_json[0]["site"]
        except:
            pass

        try:
            if get_json[0]["last_seen"]["time"] == get_json[0]["last_seen"]["time"]:
                dict["Last seen"] = datetime.utcfromtimestamp(get_json[0]["last_seen"]["time"]).strftime(
                    '%Y-%m-%d %H:%M:%S')

            if get_json[0]["last_seen"]["platform"] == get_json[0]["last_seen"]["platform"]:
                if get_json[0]["last_seen"]["platform"] == 1:
                    dict["Platform"] = "Mobile"
                if get_json[0]["last_seen"]["platform"] == 2:
                    dict["Platform"] = "iPhone"
                if get_json[0]["last_seen"]["platform"] == 3:
                    dict["Platform"] = "iPad"
                if get_json[0]["last_seen"]["platform"] == 4:
                    dict["Platform"] = "Android"
                if get_json[0]["last_seen"]["platform"] == 5:
                    dict["Platform"] = "WP"
                if get_json[0]["last_seen"]["platform"] == 6:
                    dict["Platform"] = "Windows"
                if get_json[0]["last_seen"]["platform"] == 7:
                    dict["Platform"] = "Web"
        except:
            pass

        try:
            if get_json[0]["status"] == "":
                pass
            else:
                dict["Status"] = get_json[0]["status"]
        except:
            pass

        try:
            if get_json[0]["occupation"] == get_json[0]["occupation"]:
                dict['Occupation'] = get_json[0]["occupation"]["name"]
        except:
            pass

        try:
            if get_json[0]["screen_name"] == get_json[0]["screen_name"]:
                dict["Domain"] = get_json[0]["screen_name"]
        except:
            pass

        try:
            if get_json[0]["activities"] == "":
                pass
            else:
                dict["Activities"] = get_json[0]["activities"]
        except:
            pass

        try:
            if get_json[0]["interests"] == "":
                pass
            else:
                dict["Interests"] = get_json[0]["interests"]
        except:
            pass

        try:
            if get_json[0]["music"] == "":
                pass
            else:
                dict["Music"] = get_json[0]["music"]
        except:
            pass

        try:
            if get_json[0]["movies"] == "":
                pass
            else:
                dict["Movies"] = get_json[0]["movies"]
        except:
            pass

        try:
            if get_json[0]["tv"] == "":
                pass
            else:
                dict["TV"] = get_json[0]["tv"]
        except:
            pass

        try:
            if get_json[0]["books"] == "":
                pass
            else:
                dict["Books"] = get_json[0]["books"]
        except:
            pass

        try:
            if get_json[0]["games"] == "":
                pass
            else:
                dict["Games"] = get_json[0]["games"]
        except:
            pass

        try:
            if get_json[0]["about"] == "":
                pass
            else:
                dict["About"] = get_json[0]["about"]
        except:
            pass

        try:
            if get_json[0]["quotes"] == "":
                pass
            else:
                dict["Quotes"] = get_json[0]["quotes"]
        except:
            pass

        try:
            if get_json[0]["counters"] == get_json[0]["counters"]:
                dict["Counters"] = {}
                try:
                    if get_json[0]["counters"]["albums"] == get_json[0]["counters"]["albums"]:
                        if get_json[0]["counters"]["albums"] == 0:
                            pass
                        else:
                            dict["Counters"]["Albums"] = get_json[0]["counters"]["albums"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["videos"] == get_json[0]["counters"]["videos"]:
                        if get_json[0]["counters"]["videos"] == 0:
                            pass
                        else:
                            dict["Counters"]["Videos"] = get_json[0]["counters"]["videos"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["audios"] == get_json[0]["counters"]["audios"]:
                        if get_json[0]["counters"]["audios"] == 0:
                            pass
                        else:
                            dict["Counters"]["Audios"] = get_json[0]["counters"]["audios"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["notes"] == get_json[0]["counters"]["notes"]:
                        if get_json[0]["counters"]["notes"] == 0:
                            pass
                        else:
                            dict["Counters"]["Notes"] = get_json[0]["counters"]["notes"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["friends"] == get_json[0]["counters"]["friends"]:
                        if get_json[0]["counters"]["friends"] == 0:
                            pass
                        else:
                            dict["Counters"]["Friends"] = get_json[0]["counters"]["friends"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["groups"] == get_json[0]["counters"]["groups"]:
                        if get_json[0]["counters"]["groups"] == 0:
                            pass
                        else:
                            dict["Counters"]["Groups"] = get_json[0]["counters"]["groups"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["user_videos"] == get_json[0]["counters"]["user_videos"]:
                        if get_json[0]["counters"]["user_videos"] == 0:
                            pass
                        else:
                            dict["Counters"]["User's tagged video"] = get_json[0]["counters"]["user_video"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["followers"] == get_json[0]["counters"]["followers"]:
                        if get_json[0]["counters"]["followers"] == 0:
                            pass
                        else:
                            dict["Counters"]["Followers"] = get_json[0]["counters"]["followers"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["user_photos"] == get_json[0]["counters"]["user_photos"]:
                        if get_json[0]["counters"]["user_photos"] == 0:
                            pass
                        else:
                            dict["Counters"]["User's tagged photos"] = get_json[0]["counters"]["user_photos"]
                except:
                    pass

                try:
                    if get_json[0]["counters"]["subscriptions"] == get_json[0]["counters"]["subscriptions"]:
                        if get_json[0]["counters"]["subscriptions"] == 0:
                            pass
                        else:
                            dict["Counters"]["Subscriptions"] = get_json[0]["counters"]["subscriptions"]
                except:
                    pass
        except:
            pass

        try:
            if get_json[0]["personal"] == get_json[0]["personal"]:
                dict["Personal"] = {}
                try:
                    if get_json[0]["personal"]["political"] == get_json[0]["personal"]["political"]:
                        if get_json[0]["personal"]["political"] == 1:
                            dict["Personal"]["Political"] = "Communist"
                        if get_json[0]["personal"]["political"] == 2:
                            dict["Personal"]["Political"] = "Socialist"
                        if get_json[0]["personal"]["political"] == 3:
                            dict["Personal"]["Political"] = "Moderate"
                        if get_json[0]["personal"]["political"] == 4:
                            dict["Personal"]["Political"] = "Liberal"
                        if get_json[0]["personal"]["political"] == 5:
                            dict["Personal"]["Political"] = "Conservative"
                        if get_json[0]["personal"]["political"] == 6:
                            dict["Personal"]["Political"] = "Monarchist"
                        if get_json[0]["personal"]["political"] == 7:
                            dict["Personal"]["Political"] = "Ultraconservative"
                        if get_json[0]["personal"]["political"] == 8:
                            dict["Personal"]["Political"] = "Apathetic"
                        if get_json[0]["personal"]["political"] == 9:
                            dict["Personal"]["Political"] = "Libertian"
                except:
                    pass

                try:
                    if get_json[0]["personal"]["langs"] == get_json[0]["personal"]["langs"]:
                        dict["Personal"]["Langs"] = get_json[0]["personal"]["langs"]
                except:
                    pass
                try:
                    if get_json[0]["personal"]["religion"] == get_json[0]["personal"]["religion"]:
                        dict["Personal"]["Religion"] = get_json[0]["personal"]["religion"]
                except:
                    pass

                try:
                    if get_json[0]["personal"]["inspired_by"] == get_json[0]["personal"]["inspired_by"]:
                        dict["Personal"]["Inspirted by"] = get_json[0]["personal"]["inspired_by"]
                except:
                    pass

                try:
                    if get_json[0]["personal"]["people_main"] == get_json[0]["personal"]["people_main"]:
                        if get_json[0]["personal"]["people_main"] == 1:
                            dict["Personal"]["People main"] = "Intellect and creativity"
                        if get_json[0]["personal"]["people_main"] == 2:
                            dict["Personal"]["People main"] = "Kindness and honesty"
                        if get_json[0]["personal"]["people_main"] == 3:
                            dict["Personal"]["People main"] = "Health and beauty"
                        if get_json[0]["personal"]["people_main"] == 4:
                            dict["Personal"]["People main"] = "Wealth and power"
                        if get_json[0]["personal"]["people_main"] == 5:
                            dict["Personal"]["People main"] = "Courage and persistance"
                        if get_json[0]["personal"]["people_main"] == 6:
                            dict["Personal"]["People main"] = "Humor and love for life"
                except:
                    pass

                try:
                    if get_json[0]["personal"]["life_main"] == get_json[0]["personal"]["life_main"]:
                        if get_json[0]["personal"]["life_main"] == 1:
                            dict["Personal"]["Life main"] = "Family and children"
                        if get_json[0]["personal"]["life_main"] == 2:
                            dict["Personal"]["Life main"] = "Career and money"
                        if get_json[0]["personal"]["life_main"] == 3:
                            dict["Personal"]["Life main"] = "Entertainment and leisure"
                        if get_json[0]["personal"]["life_main"] == 4:
                            dict["Personal"]["Life main"] = "Science and research"
                        if get_json[0]["personal"]["life_main"] == 5:
                            dict["Personal"]["Life main"] = "Improving the world"
                        if get_json[0]["personal"]["life_main"] == 6:
                            dict["Personal"]["Life main"] = "Personal development"
                        if get_json[0]["personal"]["life_main"] == 7:
                            dict["Personal"]["Life main"] = "Beauty and art"
                        if get_json[0]["personal"]["life_main"] == 8:
                            dict["Personal"]["Life main"] = "Fame and influence"
                except:
                    pass

                try:
                    if get_json[0]["personal"]["smoking"] == get_json[0]["personal"]["smoking"]:
                        if get_json[0]["personal"]["smoking"] == 1:
                            dict["Personal"]["Smoking"] = "Very negative"
                        if get_json[0]["personal"]["smoking"] == 2:
                            dict["Personal"]["Smoking"] = "Negative"
                        if get_json[0]["personal"]["smoking"] == 3:
                            dict["Personal"]["Smoking"] = "Neutral"
                        if get_json[0]["personal"]["smoking"] == 4:
                            dict["Personal"]["Smoking"] = "Compromisable"
                        if get_json[0]["personal"]["smoking"] == 5:
                            dict["Personal"]["Smoking"] = "Positive"
                except:
                    pass

                try:
                    if get_json[0]["personal"]["alcohol"] == get_json[0]["personal"]["alcohol"]:
                        if get_json[0]["personal"]["alcohol"] == 1:
                            dict["Personal"]["Alcohol"] = "Very negative"
                        if get_json[0]["personal"]["alcohol"] == 2:
                            dict["Personal"]["Alcohol"] = "Negative"
                        if get_json[0]["personal"]["alcohol"] == 3:
                            dict["Personal"]["Alcohol"] = "Neutral"
                        if get_json[0]["personal"]["alcohol"] == 4:
                            dict["Personal"]["Alcohol"] = "Compromisable"
                        if get_json[0]["personal"]["alcohol"] == 5:
                            dict["Personal"]["Alcohol"] = "Positive"
                except:
                    pass

            if len(dict["Personal"]) == 0:
                del dict["Personal"]

        except:
            pass

        try:
            if len(get_json[0]["mobile_phone"]) == 0:
                pass
            else:
                dict["Mobile"] = get_json[0]["mobile_phone"]
        except:
            pass

        try:
            if len(get_json[0]["home_phone"]) == 0:
                pass
            else:
                dict["Home phone"] = get_json[0]["home_phone"]
        except:
            pass

        try:
            if get_json[0]["skype"] == get_json[0]["skype"]:
                dict["Skype"] = get_json[0]["skype"]
        except:
            pass

        try:
            if get_json[0]["instagram"] == get_json[0]["instagram"]:
                dict["Instagram"] = "instagram.com/" + get_json[0]["instagram"]
        except:
            pass

        try:
            if get_json[0]["twitter"] == get_json[0]["twitter"]:
                dict["Twitter"] = "twitter.com/" + get_json[0]["twitter"]
        except:
            pass

        try:
            if get_json[0]["livejournal"] == get_json[0]["livejournal"]:
                dict["LiveJournal"] = get_json[0]["livejournal"] + ".livejournal.com"
        except:
            pass

        try:
            if get_json[0]["facebook"] == get_json[0]["facebook"]:
                dict["Facebook"] = "facebook.com/profile.php?id=" + get_json[0]["facebook"]
            else:
                pass
        except:
            pass

        try:
            if get_json[0]["country"]["title"] == get_json[0]["country"]["title"]:
                dict["Country"] = get_json[0]["country"]["title"]
        except:
            pass

        try:
            if get_json[0]["city"]["title"] == get_json[0]["city"]["title"]:
                dict["City"] = get_json[0]["city"]["title"]
        except:
            pass

        try:
            if get_json[0]["home_town"] == "":
                pass
            else:
                dict["Hometown"] = get_json[0]["home_town"]
        except:
            pass

        try:
            if len(get_json[0]["reg_date"]) == 0:
                pass
            else:
                dict["Registered"] = get_json[0]["reg_date"]
        except:
            pass

        try:
            full_size_ava = max(get_json[0]["crop_photo"]["photo"]['sizes'],
                                key=lambda line: int(line['width']))
            dict["Full-size avatar"] = full_size_ava['url']
        except:
            pass

        try:
            if get_json[0]["crop_photo"]["photo"]["date"] == get_json[0]["crop_photo"]["photo"]["date"]:
                dict["Date of avatar"] = datetime.utcfromtimestamp(get_json[0]["crop_photo"]["photo"]["date"]).strftime(
                    '%Y-%m-%d %H:%M:%S')
        except:
            pass

        try:
            if not len(get_json[0]["university_name"]):
                pass
            else:
                dict["Education"] = {}
                dict["Education"]["University"] = get_json[0]["university_name"]

            if not len(get_json[0]["faculty_name"]):
                pass
            else:
                dict["Education"]["Faculty"] = {}
                dict["Education"]["Faculty"] = get_json[0]["faculty_name"]

            if get_json[0]["graduation"] == get_json[0]["graduation"]:
                dict["Education"]["Graduation"] = {}
                dict["Education"]["Graduation"] = get_json[0]["graduation"]
            else:
                pass

            if not len(get_json[0]["education_form"]):
                pass
            else:
                dict["Education"]["Form"] = {}
                dict["Education"]["Form"] = get_json[0]["education_form"]

            if not len(get_json[0]["education_status"]):
                pass
            else:
                dict["Education"]["Status"] = {}
                dict["Education"]["Status"] = get_json[0]["education_status"]

        except:
            pass

        dict = json.dumps(dict, indent=2, ensure_ascii=False)

        ''' replacing block '''
        for i in settings.TO_REMOVE:
            dict = dict.replace(i, '')
        ''' replacing block '''

        ready_text = util.split_string(dict, 4096)

        bot.send_message(message.from_user.id,
                         "⌛ Requested info for " + at_text.lower() + " on " + str(
                             datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")) + " UTC")

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
