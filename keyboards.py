
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from models import get_setting, all_chats

main_menu = [
    [
        '🏠Home'
    ],
    [
        '⚙️Settings'
    ],
    [
        'Channels'
    ],
    [
        'Help'
    ]

]


main_menu_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)


def channel_group_show(chat_id):
    print("chat_id", chat_id)
    show_btn = [
        [
            InlineKeyboardButton('Delete', callback_data=f"delete{chat_id}"),
            InlineKeyboardButton('Back', callback_data="back")
        ]
    ]
    return InlineKeyboardMarkup(show_btn)


def status_inline_btn():
    bot_status_inline_btn = []
    sett = get_setting()
    if(sett['status']):
        bot_status_inline_btn.append(
            [
                InlineKeyboardButton(f'✅ ON', callback_data='1')
            ],
        )

        bot_status_inline_btn.append(
            [
                InlineKeyboardButton(f'OFF', callback_data='0')
            ]
        )
    if(not sett['status']):
        bot_status_inline_btn.append(
            [
                InlineKeyboardButton(f'ON', callback_data='1')
            ]
        )
        bot_status_inline_btn.append(
            [
                InlineKeyboardButton(f'✅ OFF', callback_data='0')
            ]
        )

    return InlineKeyboardMarkup(bot_status_inline_btn)


def list_channel_group():
    chats = all_chats()
    l = []
    for _chat in chats:
        l.append([
            InlineKeyboardButton(
                f"{_chat['title']}", callback_data=f"{_chat['id']}")
        ])
    return InlineKeyboardMarkup(l)
