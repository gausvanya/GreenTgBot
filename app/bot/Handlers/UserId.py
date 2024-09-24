from aiogram.types import Message
from aiogram import Router

from ..Filters import GetUserInfo, Command #, IsAdminFilter
from ..utils import get_user_mention

rt = Router()


@rt.message(Command(
    commands=['ид', 'айди', 'мой ид'],
    html_parse_mode=True)
)
async def user_id_handler(message: Message, args=None) -> None | Message:
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

    split = args[0].split('\n', 1)[0]

    if len(split.split()) == 2 and split.startswith('мой ид') or len(split.split()) == 1 and not message.reply_to_message:
        from_user = message.from_user
        user_id, user_username, user_full_name = from_user.id, from_user.username, from_user.full_name
    else:
        if len(split.split()) > 1:
            user = GetUserInfo(split.split(maxsplit=1)[1].rstrip())
            user = await user(message)

            if not user:
                return

            user_id, user_username, user_full_name = user

        elif message.reply_to_message:
            reply_user = message.reply_to_message.from_user
            user_id, user_username, user_full_name = reply_user.id, reply_user.username, reply_user.full_name
        else:
            return

    user_mention = get_user_mention(user_id, user_username, user_full_name)

    await message.reply(f'🆔 {user_mention}: <code>@{user_id}</>')
