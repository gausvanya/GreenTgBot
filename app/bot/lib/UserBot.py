from pyrogram import Client
from pyrogram.types import User, Chat

from app.config import pyrogram_config

cfg = pyrogram_config()
app = Client(name='my_account', api_id=cfg["API_ID"], api_hash=cfg["API_HASH"])


async def start_userbot() -> None:
    if not app.is_connected:
        await app.start()


async def stop_userbot() -> None:
    if app.is_connected:
        await app.stop()


async def get_user(user: str | int | list) -> User | None:
    if isinstance(user, list):
        user_id = user[0]
        user_username = user[1]
    else:
        user_id = user
        user_username = user

    try:
        user = await app.get_users(user_username)
        return user
    except Exception:
        try:
            user = await app.get_users(user_id)
            return user
        except:
            return None


async def get_chat(chat: str) -> Chat | None:
    try:
        chat = await app.get_chat(chat)
        return chat
    except:
        return None



async def get_user_info(user: str | int) -> list[str] | None:
    user = await get_user(user)
    if not user:
        return None

    user_info = [user.id, user.username, f'{user.first_name or ""} {user.last_name or ""}']
    return user_info


async def get_user_status(user: str | int | list, return_date_str: bool = None) -> str | None:
    user = await get_user(user)
    if not user:
        return 'недавно'

    user_statuses = {
        'ONLINE': 'онлайн',
        'OFFLINE': 'оффлайн',
        'RECENTLY': 'был недавно',
        'LAST_WEEK': 'на прошлой неделе',
        'LAST_MONTH': 'в прошлом месяце',
        'LONG_AGO': 'давно'
    }

    user_status = user.status
    if user_status:
        translate_status = user_statuses[user_status.name]
    else:
        translate_status = 'недавно'

    try:
        if user_status.ONLINE and user.last_online_date and return_date_str:
            date = user.last_online_date
            return f'{translate_status} ({date.day:02d}.{date.month:02d}.{date.year} {date.hour:02d}:{date.minute:02d})'
    except:
        pass

    return translate_status
