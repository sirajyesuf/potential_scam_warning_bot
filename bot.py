from html import entities
from pickle import TRUE
from pyrogram import Client, filters, errors
import config
from decorators import bot_owners_only, bot_status_on
import logging
from keyboards import main_menu_markup, status_inline_btn, list_channel_group, channel_group_show
from models import *

log_format = logging.Formatter(
    "%(asctime)s - [%(name)s] [%(levelname)s]  %(message)s")
logger = logging.getLogger()
# logging.getLogger('pyrogram').setLevel(logging.CRITICAL)

logger.setLevel(logging.INFO)
file_logger = logging.FileHandler("log")
file_logger.setLevel(logging.INFO)
file_logger.setFormatter(log_format)
logger.addHandler(file_logger)
console_logger = logging.StreamHandler()
console_logger.setFormatter(log_format)
console_logger.setLevel(logging.INFO)
logger.addHandler(console_logger)
api_id = config.API_ID
api_hash = config.API_HASH

user = Client("user", api_id=api_id, api_hash=api_hash)
bot = Client('bot',
             api_id=api_id,
             api_hash=api_hash,
             bot_token=config.BOT_TOKEN)

contract_keyword = ['Address:']
project_keyword = [
    'Contract Verified:', 'Liquidity Locked:', 'Token Launching:',
    'New Token Deployed:'
]
title_keywords = [
    'Rugpull', 'Honeypot', 'Balance Swapper', 'Liquidity Drainer',
    'Hidden Mint', 'High Tax Option', 'Potential Honeypot'
]

link_keywords = ['Explore:', 'Telegram?']
tg_not_found = "Explore: Telegram 🤷‍"
scamcode_keywords = ['Scam Check:', 'scam code detected']

images = ['Hidden Mint', 'Honeypot', 'Liquidity Drainer', 'Potential Honeypot']


def get_telegram_link(caption_entities):
    for en in caption_entities:
        if (en.type == 'text_link' and en.url.count('/') == 3):
            return en.url


def clean_signal(signal):
    signal = signal.split("\n")
    for i in signal:
        if (i == ""):
            signal.remove(i)
    return signal


def get_dict(message):
    caption = clean_signal(message.caption)
    dict = {}
    dict['link'] = "Telegram not found."
    for i in caption:
        if ([kw for kw in title_keywords if kw in i]):
            dict['title'] = dict['title'] = i[i.index('(') + 1:i.index(')')]
            dict['image'] = dict['title'] if dict['title'] in images else None
        if ([kw for kw in project_keyword if kw in i]):
            dict['project'] = i.split(":")[1].strip()
        if ([kw for kw in contract_keyword if kw in i]):
            dict['contract'] = i.split(":")[1].strip()
        if (len([kw for kw in link_keywords if kw in i]) == 2
                and tg_not_found not in i):
            dict['link'] = get_telegram_link(message.caption_entities)
    return dict


def get_out_put_signal(message):
    dict = get_dict(message)
    sett = get_setting()
    _header = "🚨<u><b>POTENTIAL SCAM WARNING</b></u>🚨"
    _title = f"<b>{dict['title']} code in contract</b>"
    _project = f"<b>Project: {dict['project']}</b>"
    _contract = f"<b>Contract:</b> {dict['contract']}"
    _link = f"<b>Link:</b> {dict['link']}"
    _bottom = sett['template']
    return dict[
        'image'], f"{_header}\n\n{_title}\n\n{_project}\n\n{_link}\n{_contract}\n\n{_bottom}"


@user.on_message(filters.chat(config.SOURCE_CHANNEL) & filters.forwarded)
@bot_status_on
def scam_check(user, message):
    if ([kw for kw in title_keywords if kw in message.caption]
            and [kw for kw in scamcode_keywords if kw in message.caption]
            and [kw for kw in link_keywords if kw in message.caption]):
        image, caption = get_out_put_signal(message)
        destinations = all_chats()
        if (image):
            for des in destinations:
                bot.send_photo(chat_id=int(des['id']),
                               photo='/asset/{image}.png',
                               caption=caption,
                               disable_web_page_preview=True,
                               parse_mode='html')
        else:
            for des in destinations:
                bot.send_message(chat_id=int(des['id']),
                                 text=caption,
                                 disable_web_page_preview=True,
                                 parse_mode='html')
        print("successfull forwarding....")
    else:
        print("ignore the signal")


@bot.on_message(filters.command('start') | filters.regex('🏠Home'))
@bot_owners_only
def start(bot, message):
    bot.send_message(chat_id=message.from_user.id,
                     text=f"Hello {message.from_user.first_name}!👋",
                     reply_markup=main_menu_markup)


@bot.on_message(filters.regex('⚙️Settings'))
def settings(bot, message):
    sett = get_setting()
    reply_markup = status_inline_btn()
    note = "✅ bot forwarding enabled."
    if (not sett['status']):
        note = "❌ bot forwarding disabled."
    bot.send_message(
        chat_id=message.from_user.id,
        text=f"⚙️Setting\n\n{note}\n\n👇set the status of the bot.",
        reply_markup=reply_markup)


static_data_filter = filters.create(
    lambda _, __, query: query.data in ["0", "1"])


@bot.on_callback_query(static_data_filter)
def set_bot_status_setting(bot, callback_query):
    # callback_query.answer(
    #     f"{callback_query.data}")
    update_bot_status(int(callback_query.data))
    reply_markup = status_inline_btn()
    sett = get_setting()
    note = "✅ bot forwarding enabled."
    if (not sett['status']):
        note = "❌ bot forwarding disabled."
    bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=f"⚙️Setting\n\n{note}\n\n👇set the status of the bot.",
        reply_markup=reply_markup)


@bot.on_message(filters.regex('Channels'))
def list_chats(bot, message):
    reply_markup = list_channel_group()
    if (reply_markup['inline_keyboard']):
        bot.send_message(chat_id=message.from_user.id,
                         text="list of channel/group",
                         reply_markup=reply_markup)
    else:
        bot.send_message(
            chat_id=message.from_user.id,
            text=
            "No channel or group.\nyou can create by using the command below\n\n /addgroup username",
        )


@bot.on_callback_query(filters.regex('^-.*$'))
def show_chat(bot, callback_query):
    chat_id = callback_query.data
    _chat = get_chat(chat_id)
    text = f"{_chat['type']} Detail\n\nID= {_chat['id']}\nTitle= {_chat['title']}\nUsername: @{_chat['username']}"
    bot.edit_message_text(chat_id=callback_query.from_user.id,
                          message_id=callback_query.message.message_id,
                          text=text,
                          reply_markup=channel_group_show(_chat['id']))


@bot.on_callback_query(filters.regex('back|^delete-.*$'))
def delete_back(bot, callback_query):
    if (callback_query.data == 'back'):
        reply_markup = list_channel_group()
        if (reply_markup['inline_keyboard']):
            bot.edit_message_text(chat_id=callback_query.from_user.id,
                                  message_id=callback_query.message.message_id,
                                  text="list of channel/group",
                                  reply_markup=reply_markup)
        else:
            bot.edit_message_text(
                chat_id=callback_query.from_user.id,
                message_id=callback_query.message.message_id,
                text=
                "No channel or group.\nyou can create by using the command below\n\n /addgroup username",
            )
    if ('delete' in callback_query.data):
        chat_id = f"-{callback_query.data.split('-')[1]}"
        delete_chat(chat_id)
        reply_markup = list_channel_group()
        if (reply_markup['inline_keyboard']):
            bot.edit_message_text(chat_id=callback_query.from_user.id,
                                  message_id=callback_query.message.message_id,
                                  text="list of channel/group",
                                  reply_markup=reply_markup)
        else:
            bot.edit_message_text(
                chat_id=callback_query.from_user.id,
                message_id=callback_query.message.message_id,
                text=
                "No channel or group.\nyou create just by forwarding any post from the channel or group to this bot.",
            )


@bot.on_message(filters.command('addgroup'))
def add_group_chat(bot, message):
    username = message.text.split(" ")[1]
    _chat = bot.get_chat(username)
    data = {
        'id': _chat.id,
        'type': _chat.type,
        'title': _chat.title,
        'username': _chat.username
    }
    if (store_chats(data)):
        text = f"✅ the {_chat.type} @{_chat.username} created sucessfully."

    else:
        text = f"❌ the {_chat.type} @{_chat.username} already created sucessfully."

    bot.send_message(
        chat_id=message.from_user.id,
        text=text,
    )


@bot.on_message(filters.regex('Help'))
def help(bot, message):
    text = "HELP\n\n/addgroup username 👈 to add destination channel or group.\n/template 👈to update the template"
    bot.send_message(
        chat_id=message.from_user.id,
        text=text,
    )


@bot.on_message(filters.command('template'))
def template(bot, message):
    sett = get_setting()
    text = f"if you want to change this template just enter the new one\n if not /cancel \n\n{sett['template']}"
    bot.send_message(chat_id=message.from_user.id,
                     text=text,
                     disable_web_page_preview=True,
                     parse_mode='html')
    conv = {'que': '/template', 'ans': 'update_template'}
    create_conv(conv)


@bot.on_message(filters.text
                & ~filters.command(['cancel', 'template', 'addgroup']))
def all_text(bot, message):
    conv = get_conv()
    # print(conv)
    # OrderedDict([('id', 1), ('que', '/template'), ('ans', 'update_template')])
    if (conv and conv['que'] == '/template'):
        text = message.text
        entities = message.entities
        if (entities):
            for ent in entities:
                if (ent['type'] == 'text_link'):
                    start = ent['offset']
                    end = ent['offset'] + ent['length']
                    old = text[start:end]
                    new = f"<a href='{ent['url']}'>{old}</a>"
                    text = text.replace(old, new)
        update_template(text)
        bot.send_message(
            chat_id=message.from_user.id,
            text="the template succesfully updated.",
        )
        delete_conv()
        return


@bot.on_message(filters.command('cancel'))
def cancel(bot, message):
    delete_conv()
    bot.send_message(
        chat_id=message.from_user.id,
        text="cancelled.",
    )


# seed settings
_channel = "<a href='https://t.me/shartanentryportal'>SHARTAN ARMY</a>"
_bottom = f"Ask the dev BEFORE buying!\nDon't get trapped!\n\n{_channel} $SHARTAN #NFA"

if (get_setting() == None):
    sett = {'status': True, 'template': _bottom}
    store_setting(sett)
logger.info('POTENTIAL SCAM WARNING BOT START 🚀')
user.start()
bot.run()
