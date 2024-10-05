from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..DataBase.Models import AntiSpam, Ignore, Bans, User
from ..Filters import Command, GetUserInfo, IsAgentFilter
from ..utils import get_user_mention

rt = Router()


@rt.message(Command(
    commands=['+ас'],
    html_parse_mode=True),
    IsAgentFilter()
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
    IsAgentFilter()
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
    IsAgentFilter()
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
    IsAgentFilter()
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
    IsAgentFilter()
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
        text += f'{data_str} | {chat_name} | {reason} | {time_int} {time_type}\n'

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



@rt.message(Command(
    commands=['вносы от']),
    IsAgentFilter()
)
async def ac_list_for_agent(message: Message):
    if message.entities:
        entities = message.entities[0]

        if entities.url:
            user_info = entities.url
        elif entities.user:
            user_info = f'@{entities.user.id}'
        elif entities.type == 'mention':
            user_info = next((word for word in message.text.split('\n', 1)[0].split() if word.startswith('@')),
                             None)
        else:
            user_info = None

        if user_info:
            user = await GetUserInfo(user_info)(message)
            if not user:
                return
            agent_id = user[0]
        else:
            return

    elif message.reply_to_message:
        agent_id = message.reply_to_message.from_user.id
    else:
        return

    await send_ac_list(message, 0, agent_id)


async def send_ac_list(message: Message, offset: int, agent_id: int, callback_query: CallbackQuery = None):
    antispams = await AntiSpam.filter(admin_id=agent_id).limit(10).offset(offset)
    agent = await User.filter(id=agent_id).first()
    user_mention = get_user_mention(agent.id, agent.username, agent.full_name)

    text_ac = f'<b>Список пользователей которых внес агент {user_mention}:</>\n'
    if antispams:
        for antispam in antispams:
            user = await User.get_or_none(id=antispam.user_id)
            user_mention = get_user_mention(antispam.user_id, user.username, user.full_name)
            ignore = await Ignore.filter(user_id=antispam.user_id, activity=True).first()

            text_ac += (
                f'🔴 {user_mention}:\n'
                f'💬 <b>Причина вноса:</> {antispam.reason}\n'
                f'📛 <b>АнтиСпам статус:</> {antispam.activity}\n'
                f'🤐 <b>Игнор команд:</> {"Да" if ignore else "Нет"}\n\n'
            )

        keyboard = await page_ac_list_keyboard(offset, message, agent_id)

        if callback_query:
            await callback_query.message.edit_text(text_ac, reply_markup=keyboard.as_markup())
        else:
            await message.answer(text_ac, reply_markup=keyboard.as_markup())
    else:
        if callback_query:
            await callback_query.message.edit_text(f"{text_ac + 'Пуст.'}")
        else:
            await message.answer(f"{text_ac + 'Пуст.'}")


async def page_ac_list_keyboard(offset: int, message, agent_id: int) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()

    if offset > 0:
        keyboard.button(text='⬅️ Назад', callback_data=f'acbase_{offset - 10}_{agent_id}')
    antispams = await AntiSpam.filter(admin_id=agent_id).limit(1).offset(offset + 10)

    if len(antispams) > 0:
        keyboard.button(text='Вперед ➡️', callback_data=f'acbase_{offset + 10}_{agent_id}')
    return keyboard


@rt.callback_query(F.data.startswith('acbase_'))
async def handle_banlist_pagination(call: CallbackQuery):
    user_id = int(call.data.split('_')[2])

    if user_id != call.from_user.id:
        return await call.answer('Эта кнопочка не для вас!')

    offset = int(call.data.split('_')[1])
    await send_ac_list(call.message, offset, user_id, call)
    await call.answer()