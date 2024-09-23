from datetime import datetime

from aiogram import Router
from aiogram.types import Message

from ..DataBase.Models import AntiSpam, Ignore, Bans, User
from ..Filters import Command, GetUserInfo
from ..utils import get_user_mention

rt = Router()


@rt.message(Command(
    commands=['+ас'],
    html_parse_mode=True),
)
async def add_user_antispam_handler(message: Message, args=None) -> None | Message:

    if len(args[0].split('\n', 1)[0].split()) > 2 and args[0].split('\n', 1)[0].split()[1].lower() == 'игнор':
        user = GetUserInfo(args[0].split('\n', 1)[0].split(maxsplit=2)[2].rstrip())
        user = await user(message)

        if not user:
            return

        user_id, user_username, user_full_name = user

    elif len(args[0].split('\n', 1)[0].split()) > 1 and args[0].split('\n', 1)[0].split()[1].lower() != 'игнор':
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
    reason = args[0].split('\n', 1)[1] if len(args[0].split('\n', 1)) > 1 else 'не указана'

    antispam = await AntiSpam.get_or_none(
        user_id=user_id,
        activity=True
    )

    if antispam:
        return await message.answer('⛔️ Пользователь уже есть в базе АнтиСпам')

    if 'игнор' in args[0].split('\n', 1)[0]:
        await message.answer(f'✅ {user_mention} внесен в базу АнтиСпам с игнором команд бота')
        try:
            await message.bot.send_message(user_id, f'✅ Вы были внесены в базу АнтиСпам бота с игнором команд\n💬 Причина: {reason}')
        except:
            pass
        await Ignore.create(
            user_id=user_id,
            admin_id=message.from_user.id,
            reason=reason,
            activity=True
        )
    else:
        await message.answer(f'✅ {user_mention} внесен в базу АнтиСпам')
        try:
            await message.bot.send_message(user_id, f'✅ Вы были внесены в базу АнтиСпам бота\n💬 Причина: {reason}')
        except:
            pass

    await AntiSpam.create(
        user_id=user_id,
        admin_id=message.from_user.id,
        reason=reason,
        activity=True
    )


@rt.message(Command(
    commands=['+игнор'],
    html_parse_mode=True),
)
async def add_user_ignore_handler(message: Message, args=None):
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
    reason = args[0].split('\n', 1)[1] if len(args[0].split('\n', 1)) > 1 else 'не указана'

    ignore = await Ignore.get_or_none(
        user_id=user_id,
        activity=True
    )

    if ignore:
        return await message.answer('⛔️ Пользователь уже есть в игноре бота')

    await Ignore.create(
        user_id=user_id,
        admin_id=message.from_user.id,
        reason=reason,
        activity=True
    )

    await message.answer(f'✅ {user_mention} внесен в игнор команд бота')
    try:
        await message.bot.send_message(user_id, f'✅ Вы были внесены в игнор базу бота\n💬 Причина: {reason}')
    except:
        pass


@rt.message(Command(
    commands=['-ас'],
    html_parse_mode=True),
)
async def remove_user_antispam_handler(message: Message, args=None):
    split = args[0].split('\n', 1)[0]

    if len(args[0].split('\n', 1)[0].split()) > 2 and split.split()[1] == 'ошибка':
        user = GetUserInfo(args[0].split('\n', 1)[0].split(maxsplit=2)[2].rstrip())
        user = await user(message)

        if not user:
            return

        user_id, user_username, user_full_name = user
    elif len(args[0].split('\n', 1)[0].split()) > 1 and split.split()[1] != 'ошибка':
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


    antispam = await AntiSpam.get_or_none(
        user_id=user_id,
        activity=True
    )

    if not antispam:
        return await message.answer(f'❌ {user_mention} нету в базе АнтиСпам')

    await message.answer(f'✅ {user_mention} удален из базы АнтиСпам')
    try:
        await message.bot.send_message(user_id, '✅ Вы были удалены из АнтиСпам базы')
    except:
        pass

    if 'ошибка' in args[0].split('\n', 1)[0].lower():
        result = await AntiSpam.filter(user_id=user_id, activity=True).first()
        await result.delete()
    else:
        await AntiSpam.update_or_create(
            defaults={'activity': False,
                      'admin_id': message.from_user.id},
            user_id=user_id,
            activity=True
        )


@rt.message(Command(
    commands=['-игнор'],
    html_parse_mode=True),
)
async def remove_user_ignore_handler(message: Message, args=None):
    split = args[0].split('\n', 1)[0]

    if len(args[0].split('\n', 1)[0].split()) > 2 and split.split()[1] == 'ошибка':
        user = GetUserInfo(args[0].split('\n', 1)[0].split(maxsplit=2)[2].rstrip())
        user = await user(message)

        if not user:
            return

        user_id, user_username, user_full_name = user
    elif len(args[0].split('\n', 1)[0].split()) > 1 and split.split()[1] != 'ошибка':
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

    ignore = await Ignore.get_or_none(
        user_id=user_id,
        activity=True
    )

    if not ignore:
        return await message.answer(f'❌ {user_mention} нету в игноре бота')

    await message.answer(f'✅ {user_mention} удален из игнора бота')
    try:
        await message.bot.send_message(user_id, '✅ Вы были удалены из игнора команд бота')
    except:
        pass

    if 'ошибка' in args[0].split('\n', 1)[0].lower():
        result = await Ignore.filter(user_id=user_id, activity=True).first()
        await result.delete()
    else:
        await Ignore.update_or_create(
            defaults={'activity': False,
                      'admin_id': message.from_user.id},
            user_id=user_id,
            activity=True
        )


@rt.message(Command(
    commands=['баны'],
    html_parse_mode=True),
)
async def check_bans_user(message: Message, args=None):
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
    bans = await Bans.filter(user_id=user_id).all()

    text = f'Баны пользователя {user_mention}:\n\n'
    if not bans:
        text += '📝 Баны не найдены\n'

    for ban in bans:
        chat_id = ban.chat_id
        reason = ban.reason
        time_int = ban.time_int or ''
        time_type = ban.time_type
        current_timestamp = ban.current_timestamp

        try:
            chat_name = (await message.bot.get_chat(chat_id)).full_name
        except:
            chat_name = 'не известен'

        if current_timestamp:
            data_ban = datetime.fromtimestamp(current_timestamp)
            data_ban_day = data_ban.day
            data_ban_month = data_ban.month
            data_ban_year = data_ban.year
            data_str = f'{data_ban_day:02}.{data_ban_month:02}.{data_ban_year}'
        else:
            data_str = 'дата не известна'
        text += f'{data_str} Забанен в чате {chat_name}: {reason}, на {time_int} {time_type}\n'

    antispam_true = await AntiSpam.get_or_none(user_id=user_id, activity=True)
    ignore_true = await Ignore.get_or_none(user_id=user_id, activity=True)
    if antispam_true:
        agent_id = antispam_true.admin_id
        reason = antispam_true.reason
        agent = await User.get_or_none(id=agent_id)

        agent_mention = get_user_mention(agent_id, agent.username, agent.full_name)

        text += ("\n\n📛 Пользователь в базе АнтиСпам\n"
                 f"👤 Внес агент: {agent_mention}\n"
                 f'💬 Причина: {reason}\n')

    if ignore_true:
        agent_id = ignore_true.admin_id
        agent = await User.get_or_none(id=agent_id)
        reason = ignore_true.reason

        agent_mention = get_user_mention(agent_id, agent.username, agent.full_name)

        text += ("\n\n📛 Пользователь в игноре бота\n"
                 f'👤 Внес агент: {agent_mention}\n'
                 f'💬 Причина: {reason}\n')

    antispam_false = await AntiSpam.filter(user_id=user_id, activity=False).order_by('-id').first()
    if antispam_false:
        agent_id = antispam_false.admin_id
        reason = antispam_false.reason
        agent = await User.get_or_none(id=agent_id)
        antispam_false_count = await AntiSpam.filter(user_id=user_id, activity=False).count()

        agent_mention = get_user_mention(agent_id, agent.username, agent.full_name)

        text += (f'\n🔱 Количество выносов из АнтиСпам: {antispam_false_count}\n'
                 f'👤 Вынес агент: {agent_mention}\n'
                 f'💬 Последняя причина: {reason}\n')

    ignore_false = await Ignore.filter(user_id=user_id, activity=False).order_by('-id').first()
    if ignore_false:
        agent_id = ignore_false.admin_id
        reason = ignore_false.reason
        agent = await User.get_or_none(id=agent_id)
        antispam_false_count = await Ignore.filter(user_id=user_id, activity=False).count()

        agent_mention = get_user_mention(agent_id, agent.username, agent.full_name)

        text += (f'\n🔱 Количество выносов из игнора: {antispam_false_count}\n'
                 f'👤 Вынес агент: {agent_mention}\n'
                 f'💬 Последняя причина: {reason}\n')

    await message.answer(text)
