# 📄 VK User Info bot [Beta]
Telegram bot which uses VK API [users.get][1] method to get detailed information about user by ID.

Built by [pyTelegramBotAPI][5] and [vk][6]

Bot avaiable at [@VKUserInfo_bot][4]

`NOTICE: This bot is still work in progress. Code or design may be not optimized, some functions don't work correctly. Pull requests are welcome.`

### 🛠 Setup
You need to set variables in settings.py:
* `TELEGRAM_TOKEN` is token of Telegram bot. Create bot and get token: [@BotFather][2].
* `VK_TOKEN` is VK API [Implicit Flow][3] access_token.

While getting access token, use [all permissions][7] for better working bot


### 🔌 Run bot
* Type `python bot.py` to launch.



[1]: https://vk.com/dev/users.get "users.get method"
[2]: https://telegram.me/BotFather "Open @BotFather in Telegram"
[3]: https://vk.com/dev/implicit_flow_user?f=3.%20Receiving%20access_token "Implicit Flow for User Access Token"
[4]: https://telegram.me/VKUserInfo_bot "@VKUserInfo_bot"
[5]: https://github.com/eternnoir/pyTelegramBotAPI "pyTelegramBotAPI at Github"
[6]: https://github.com/voronind/vk "VK library at Github"
[7]: https://vk.com/dev/permissions?f=1.%20Access%20Permissions%20for%20User%20Token "Access Permissions for User Token"
