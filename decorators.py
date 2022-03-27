from functools import wraps
import config
from models import get_setting


def bot_owners_only(func):

    @wraps(func)
    def wrapper(bot, message):
        chat_id = message.from_user.id
        bot_owners = [int(i) for i in config.BOT_OWNERS.split(',')]
        print(bot_owners)
        if (int(chat_id) in bot_owners):
            return func(bot, message)
        else:
            message.reply_text(
                '❌You are not owner of the bot.stop giving me commands.')

    return wrapper


def bot_status_on(func):
    @wraps(func)
    def wrapper(bot, message):
        sett = get_setting()
        if(sett['status']):
            return func(bot, message)
        else:
            print("the bot is in OFF state")

    return wrapper
