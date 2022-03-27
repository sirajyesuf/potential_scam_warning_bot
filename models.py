from db import settings, chats, conversations


def store_setting(data):
    return settings.insert(data)


def get_setting():
    for sett in settings.all():
        return sett


def update_bot_status(value):
    setting = get_setting()
    data = dict(id=setting['id'], status=value)
    return settings.update(data, ['id'])


def update_bot_num_forwarded():
    setting = get_setting()
    data = dict(id=setting['id'], num_forwarded=int(
        setting['num_forwarded']+1))
    return settings.update(data, ['id'])


def store_chats(data):
    if(not get_chat(data['id'])):
        return chats.insert(data)


def delete_chat(id):
    return chats.delete(id=id)


def get_chat(id):
    return chats.find_one(id=id)


def all_chats():
    return chats.all()


def create_conv(data):
    return conversations.insert(data)


def get_conv():
    for conv in conversations.all():
        return conv
def delete_conv():
    return conversations.delete()


def update_template(template):
    setting = get_setting()
    data = dict(id=setting['id'], template=template)
    return settings.update(data, ['id'])
