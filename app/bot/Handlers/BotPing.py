from aiogram.types import Message
from aiogram import Router

from datetime import datetime
from ..Filters import Command, IsAdminFilter

rt = Router()


@rt.message(Command(commands=['пинг', 'ping']))
async def ping_bot_handler(message: Message, args=None):
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

    if len(args[0].split('\n', 1)[0].split()) > 1:
        return

    start_time = datetime.now()
    await message.bot.get_me()
    end_time = datetime.now()
    ping_time = (end_time - start_time).microseconds // 1000

    if ping_time < 50:
        ping_status = "скоростной"
        emoji = "🚀"
    elif 50 <= ping_time < 200:
        ping_status = "быстрый"
        emoji = "🏎"
    elif 200 <= ping_time < 500:
        ping_status = "медленный"
        emoji = "🏃‍♂‍➡️"
    else:
        ping_status = "ужасный"
        emoji = "🚶‍♂‍➡️"

    await message.answer('🏓 <b>ПОНГ!</>\n\n'
                             f'{emoji} Ответ: <b>{ping_status} | {ping_time} мс.</> ')
