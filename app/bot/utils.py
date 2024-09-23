from slugify import slugify
import re


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def get_user_mention(user_id, user_username, user_full_name) -> str:
    user_full_name = clear_text(user_full_name)
    if user_full_name == '':
        user_full_name = user_username if user_username is not None else user_id

    if user_username:
        return f'<a href="https://t.me/{user_username}">{user_full_name}</>'
    else:
        return f'<a href="tg://openmessage?user_id={user_id}">{user_full_name}</>'


def clear_text(text: str) -> str:
    cleared_text = re.sub(r'<[^>]+>', '', text)
    cleared_text = slugify(
        text=cleared_text,
        lowercase=False,
        separator=" ",
        allow_unicode=True,
    )
    return cleared_text


def get_admin_name_from_rang(rang: int) -> str:
    name_from_rang = {
        0: 'Участник',
        1: 'Модератор',
        2: 'Старший Модератор',
        3: 'Администратор',
        4: 'Старший Администратор',
        5: 'Создатель'
    }
    return name_from_rang[rang]


def get_emoji_rang_admin(rang: int) -> str:
    name_from_rang = {
        0: '0️⃣',
        1: '1️⃣',
        2: '2️⃣',
        3: '3️⃣',
        4: '4️⃣',
        5: '5️⃣'
    }
    return name_from_rang[rang]
