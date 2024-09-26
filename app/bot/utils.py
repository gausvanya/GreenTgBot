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


def vault_access_command(command: str) -> int | None:
    commands = {
        'факт': 0, 'вики': 0, 'рк': 4,
        '+приветствие': 3, '-приветствие': 3, 'приветствие': 2, 'поприветствуй': 2,
        'ид': 0, 'мой ид': 0, 'правила': 0, '+правила': 3, '-правила': 3, 'репорт': 0,
        'жалоба': 0, 'профиль': 0, 'кто ты': 0, 'кто я': 0, 'мой профиль': 0, 'заметки': 0,
        'заметка': 0, '+заметка': 3, '-заметка': 3, 'кик': 2,  'исключить': 2, 'kick': 2, 'бан': 1,
        'чс': 1, 'мут': 1, 'пин': 1, 'закреп': 1, 'откреп': 1, 'анпин': 1, 'повысить': 4, 'понизить': 4,
        'снять': 4, '+модер': 4, '-модер': 4, 'кто админ': 0, 'админы': 0, 'пинг': 0
    }

    try:
        return commands[command]
    except KeyError:
        return None
