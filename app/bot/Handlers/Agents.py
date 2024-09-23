from aiogram import Router, F
from aiogram.types import Message

from ..DataBase.Models import Agents, User
from ..Filters import GetUserInfo, Command
from ..lib.UserBot import get_user_status
from ..utils import get_user_mention

rt = Router()


@rt.message(Command(
    commands=['+агент'],
    html_parse_mode=True),
    F.from_user.id.in_({5070279413, 5858412531})
)
async def add_agent_handler(message: Message, args=None):
    if len(args[0].split('\n', 1)[0].split()) > 1:
        user = GetUserInfo(args[0].split('\n', 1)[0].split(maxsplit=1)[1].rstrip())
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
    result = await Agents.filter(user_id=user_id).first()

    if result:
        return await message.answer(f'❌ пользователь {user_mention} уже агент')

    await Agents.create(user_id=user_id, admin_id=message.from_user.id)
    await message.answer(f'✅ Пользователь {user_mention} назначен агентом')


@rt.message(Command(
    commands=['-агент'],
    html_parse_mode=True),
    F.from_user.id.in_({5070279413, 5858412531})
)
async def remove_agent_handler(message: Message, args=None):
    if len(args[0].split('\n', 1)[0].split()) > 1:
        user = GetUserInfo(args[0].split('\n', 1)[0].split(maxsplit=1)[1].rstrip())
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
    result = await Agents.filter(user_id=user_id).first()

    if not result:
        return await message.answer(f'❌ пользователь {user_mention} не агент')

    await result.delete()
    await message.answer(f'✅ Агент {user_mention} разжалован')


@rt.message(Command(
    commands=['агенты', 'кто агент'],
    html_parse_mode=True),
    F.from_user.id.in_({5070279413, 5858412531})
)
async def agent_list_handler(message: Message):
    result = await Agents.all()
    text_agents = '🔱 <b> Список агентов бота:</>\n'

    if not result:
        return await (message.answer(f"{text_agents + 'Пуст'}"))

    for agent in result:
        user = await User.get_or_none(id=agent.user_id)
        admin = await User.get_or_none(id=agent.admin_id)

        get_status = await get_user_status(user.username if user.username else user.id)
        emoji_status = '🎾' if get_status == 'онлайн' else '🏐'

        user_mention = get_user_mention(user.id, user.username, user.full_name)
        admin_mention = get_user_mention(admin.id, admin.username, admin.full_name)

        text_agents += f'{emoji_status} Агент {user_mention}. Назначил: {admin_mention}\n'

    await message.answer(text_agents)
