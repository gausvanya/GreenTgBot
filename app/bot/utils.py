import logging
from loguru import logger
from datetime import datetime

from dateutil.relativedelta import relativedelta
from slugify import slugify
import re

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


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
        'чс': 1, 'банлист': 1, 'листбанов': 1, 'причина': 1, 'разбан': 1, 'вернуть': 1, 'мут': 1, 'пин': 1,
        'закреп': 1, 'откреп': 1, 'анпин': 1, 'повысить': 4, 'понизить': 4,
        'снять': 4, '+модер': 4, '-модер': 4, 'кто админ': 0, 'админы': 0, 'пинг': 0
    }

    try:
        return commands[command]
    except KeyError:
        return None


def get_timestamp(time_int: int, time_type: str) -> datetime | bool | None | str:
    if time_type in ['минут', 'минута', 'минуты']:
        dt = datetime.now() + relativedelta(minutes=time_int)
    elif time_type in ['час', 'часа', 'часов']:
        dt = datetime.now() + relativedelta(hours=time_int)
    elif time_type in ['день', 'дня', 'дней', 'сутки', 'суток']:
        dt = datetime.now() + relativedelta(days=time_int)
    elif time_type in ['неделя', 'недели', 'недель']:
        dt = datetime.now() + relativedelta(weeks=time_int)
    elif time_type in ['месяц', 'месяца', 'месяцев']:
        dt = datetime.now() + relativedelta(months=time_int)
    elif time_type in ['год', 'года', 'лет']:
        dt = datetime.now() + relativedelta(years=time_int)
    elif time_type == 'навсегда':
        dt = 'None'
    else:
        return

    return dt


def check_time(split: str) -> list | None:
    try:
        dict_time = {
            'навсегда': [None, 'навсегда'],
            'минута': [1, 'минута'],
            'час': [1, 'час'],
            'день': [1, 'день'],
            'сутки': [1, 'день'],
            'неделя': [1, 'неделя'],
            'месяц': [1, 'месяц'],
            'год': [1, 'год']
        }

        return dict_time[split]
    except Exception:
        return
