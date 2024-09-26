from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message

from ..DataBase.Models import Agents, User
from ..Filters import GetUserInfo, Command
from ..lib.UserBot import get_user_status
from ..utils import get_user_mention

rt = Router()
agents = {5262910675, 5070279413, 5858412531}


@rt.message(Command(
    commands=['+агент', '+стагент', '+техагент', '+глагент'],
    html_parse_mode=True),
    F.from_user.id.in_(agents)
)
async def add_agent_handler(message: Message, args=None):
    split = args[0].split('\n', 1)[0].lower()

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
    date = datetime.now().timestamp()

    if split.split()[0] == '+агент':
        rang = 'агентом'
        default = {'admin_id': message.from_user.id, 'date': date}
    elif split.split()[0] == '+стагент':
        rang = 'старшим агентом'
        default = {'st_agent': True, 'admin_id': message.from_user.id, 'date': date}
    elif split.split()[0] == '+глагент':
        rang = 'главным агентом'
        default = {'gl_agent': True, 'admin_id': message.from_user.id, 'date': date}
    else:
        return

    await Agents.update_or_create(
        defaults=default,
        user_id=user_id
    )
    await message.answer(f'✅ Пользователь {user_mention} назначен {rang}')


@rt.message(Command(
    commands=['-агент', '-стагент', '-техагент', '-глагент'],
    html_parse_mode=True),
    F.from_user.id.in_(agents)
)
async def remove_agent_handler(message: Message, args=None):
    split = args[0].split('\n', 1)[0].lower()

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


    if split.split()[0] == '-стагент':
        rang = 'старший агент'
        default = {'st_agent': None, 'admin_id': message.from_user.id}
    elif split.split()[0] == '-глагент':
        rang = 'главный агент'
        default = {'gl_agent': None, 'admin_id': message.from_user.id}
    else:
        default = None

        result = await Agents.filter(user_id=user_id).first()
        if not result:
            return await message.answer(f'{user_mention} не является агентом')

        await message.answer(f'✅ Агент {user_mention} разжалован')
        await result.delete()

    if default:
        await Agents.update_or_create(
            defaults=default,
            user_id=user_id
        )
        await message.answer(f'✅ {rang} {user_mention} разжалован')


@rt.message(Command(
    commands=['агенты', 'кто агент'],
    html_parse_mode=True),
    F.from_user.id.in_(agents)
)
async def agent_list_handler(message: Message):
    result = await Agents.all()
    text_agents = '🔱 <b>Список агентов бота:</>\n'

    if not result:
        return await (message.answer(f"{text_agents + 'Пуст'}"))


    for agent in result:
        if agent.gl_agent:
            rang = 'Гл.Агент'
        elif agent.st_agent:
            rang = 'Ст.Агент'
        else:
            rang = 'Агент'

        user = await User.get_or_none(id=agent.user_id)

        get_status = await get_user_status(user.username if user.username else user.id)
        emoji_status = '🎾' if get_status == 'онлайн' else '🏐'

        user_mention = get_user_mention(user.id, user.username, user.full_name)

        text_agents += f'{emoji_status} {rang} {user_mention}\n'

    await message.answer(text_agents)


@rt.message(Command(
    commands=['агент инфо'],
    html_parse_mode=True),
    F.from_user.id.in_(agents)
)
async def remove_agent_handler(message: Message, args=None):
    split = args[0].split('\n', 1)[0].lower()

    if len(split.split()) > 1:
        user = GetUserInfo(split.split(maxsplit=2)[2].rstrip())
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
        return await message.answer(f'{user_mention} не является агентом')

    admin = await User.filter(id=result.admin_id).first()

    admin_mention = get_user_mention(admin.id, admin.username, admin.full_name)


    if result.date:
        date = datetime.fromtimestamp(float(result.date))
        date = f'{date.day:02d}.{date.month:02d}.{date.year} {date.hour:02d}:{date.minute:02d}'
    else:
        date = 'неизвестная дата'

    if result.gl_agent:
        rang = 'Гл.Агент'
        capability = (
            '➕ Возможность внесения в антиспам / игнор в любых чатах\n'
            '➕ Возможность вынесения из антиспам / игнор в любых чатах\n'
            '➕ Возможность назначения ранга в чужих чатах\n'
            '➕ Возможность назначения/разжалования агентов\n'
        )
    elif result.st_agent:
        rang = 'Ст.Агент'
        capability = (
            '➕ Возможность внесения в антиспам / игнор в любых чатах\n'
            '➕ Возможность вынесения из антиспам / игнор в любых чатах\n'
            '➕ Возможность назначения ранга в чужих чатах\n'
        )
    else:
        rang = 'Обычный Агент'
        capability = (
            '➕ Возможность внесения в антиспам / игнор в агент-чате\n'
            '➕ Возможность вынесения из антиспам / игнор в агент-чате\n'
        )

    await message.answer(
        f'👤 это агент {user_mention}:\n\n'
        f'Ранг: {rang}\n'
        f'Возможности:\n{capability}\n\n'
        f'Назначил: {admin_mention}\n'
        f'Дата назначения: {date}'
    )