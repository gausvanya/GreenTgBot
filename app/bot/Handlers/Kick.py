from aiogram.types import Message
from aiogram import Router, F

from ..Filters import GetUserInfo, Command, IsAdminFilter
from ..utils import get_user_mention

import asyncio

rt = Router()


@rt.message(Command(
    commands=['кик', 'исключить'],
    html_parse_mode=True),
    F.chat.type != 'private',
)
async def kick_user_handler(message: Message, args=None) -> None | Message:
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

    if message.entities:
        entities = message.entities[0]

        if entities.url:
            user_info = entities.url
        elif entities.user:
            user_info = f'@{entities.user.id}'
        elif entities.type == 'mention':
            user_info = next((word for word in message.text.split('\n', 1)[0].split() if word.startswith('@')), None)
        else:
            user_info = None

        if user_info:
            user = await GetUserInfo(user_info)(message)
            if not user:
                return
            user_id, user_username, user_full_name = user
        else:
            return

    elif message.reply_to_message:
        reply_user = message.reply_to_message.from_user
        user_id, user_username, user_full_name = reply_user.id, reply_user.username, reply_user.full_name
    else:
        return

    user_mention = get_user_mention(user_id, user_username, user_full_name)
    chat_member = await message.bot.get_chat_member(message.chat.id, user_id)

    if chat_member.status in ['left', 'kicked']:
        return await message.answer(f'❌ Пользователь {user_mention} покинул чат или ранее был уже исключен')

    try:
        await message.bot.ban_chat_member(message.chat.id, user_id)
        await message.reply(f'✅ Пользователь {user_mention} исключен из чата')
        await asyncio.sleep(60)

        if chat_member.status != 'kicked':
            return

        await message.bot.unban_chat_member(message.chat.id, user_id)
    except Exception as e:
        if chat_member.status in ['administrator', 'creator']:
            return await message.answer(
                f'❌ Пользователь {user_mention} является администратором чата и не может быть ограничен'
            )

        return await message.answer(f'❗️ Произошла ошибка при попытке исключить пользователя:\n<b>{e}</>')
