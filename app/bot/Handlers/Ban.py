from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F, Bot

from ..Filters import GetUserInfo, IsAdminFilter, Command
from ..utils import get_user_mention, check_time, get_timestamp, get_admin_name_from_rang
from ..DataBase.Models import Bans, User, ChatSettings, Admins, AntiSpam

from datetime import datetime
import asyncio

rt = Router()


async def check_activity_bans(bot: Bot) -> None:
    while True:
        current_time = datetime.now().timestamp()
        get_bans = await Bans.filter(timestamp__isnull=False).all()

        if get_bans:
            for ban in get_bans:
                timestamp = ban.timestamp

                if current_time >= timestamp:
                    user_id = ban.user_id
                    admin_id = ban.admin_id
                    chat_id = ban.chat_id
                    reason = ban.reason
                    current_timestamp = ban.current_timestamp

                    data_ban = datetime.fromtimestamp(current_timestamp)
                    data_ban_day = data_ban.day
                    data_ban_month = data_ban.month
                    data_ban_year = data_ban.year
                    data_str = f'{data_ban_day:02}.{data_ban_month:02}.{data_ban_year}'

                    user = await User.get_or_none(id=user_id)
                    admin = await User.get_or_none(id=admin_id)

                    user_mention = get_user_mention(user_id, user.username, user.full_name)
                    admin_mention = get_user_mention(admin_id, admin.username, admin.full_name)

                    await ban.delete()

                    await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
                    await bot.send_message(
                        chat_id=chat_id,
                        text=(f'🛑 Пользователь {user_mention} разбанен\n'
                              f'👤 Он был забанен модератором: {admin_mention}\n'
                              f'💬Причина: {reason}\n'
                              f'📅 Дата бана: {data_str}')
                    )

            await asyncio.sleep(60)


@rt.message(Command(
    commands=['бан период', 'баны период']),
    F.chat.type != 'private',
)
async def add_default_time_ban(message: Message, args=None) -> None | Message:
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

    split = args[0].split('\n', 1)[0].split()

    if len(split) == 3 and split[2] == 'навсегда':
        time_int, time_type = None, 'навсегда'
    elif len(split) == 3 and split[2] in {'минута', 'час', 'день', 'сутки', 'неделя', 'месяц', 'год'}:
        time_int, time_type = 1, split[2]
    elif len(split) == 4 and split[2].isnumeric() and split[3] in {
        'минут', 'минута', 'минуты',
        'час', 'часа', 'часов',
        'день', 'дня', 'дней',
        'неделя', 'недели', 'недель',
        'месяц', 'месяца', 'месяцев',
        'год', 'года', 'лет'
    }:
        time_int, time_type = split[2], split[3]
    else:
        return

    if not time_int:
        data = 'навсегда'
        time_msg = 'навсегда'
    else:
        data = f'{time_int}_{time_type}'
        time_msg = f'{time_int} {time_type}'

    await ChatSettings.update_or_create(
        defaults={'default_time_ban': data},
        chat_id=message.chat.id
    )

    await message.answer(f'Время бана по умолчанию установлено на: {time_msg}')


@rt.message(Command(
    commands=['бан', 'чс'],
    html_parse_mode=True),
    F.chat.type != 'private'
)
async def ban_user(message: Message, args=None) -> None | Message:
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

    chat_id = message.chat.id
    split =  args[0].split('\n', 1)[0].split()
    startswith_url_user = ('<a', '@', 'https://t.me/', 'tg://', 't.me/')
    split_user = None

    if len(split) >= 4 and split[1].isdigit():
        time_int, time_type = split[1], split[2]
        split_user = args[0].split('\n', 1)[0].split(maxsplit=3)[3].rstrip()

    elif len(split) >= 3 and check_time(split[1]):
        result_time = check_time(split[1])
        time_int, time_type = result_time[0], result_time[1]
        split_user = args[0].split('\n', 1)[0].split(maxsplit=2)[2].rstrip()

    elif len(split) >= 2 and split[1].startswith(startswith_url_user):
        default_time = await ChatSettings.filter(chat_id=chat_id).first()
        if default_time.default_time_ban == 'навсегда':
            time_int, time_type = None, 'навсегда'
        else:
            default_time_split = default_time.default_time_ban.split('_')
            time_int, time_type = default_time_split[0], default_time_split[1]

        split_user = args[0].split('\n', 1)[0].split(maxsplit=1)[1].rstrip()

    elif message.reply_to_message:
        reply_user = message.reply_to_message.from_user
        user_id, user_username, user_full_name = reply_user.id, reply_user.username, reply_user.full_name

        if len(split) == 1:
            default_time = await ChatSettings.filter(chat_id=chat_id).first()

            if default_time.default_time_ban == 'навсегда':
                time_int, time_type = None, 'навсегда'
            else:
                default_time_split = default_time.default_time_ban.split('_')
                time_int, time_type = default_time_split[0], default_time_split[1]

        elif len(split) == 2 and check_time(split[1]):
            result = check_time(split[1])
            time_int, time_type = result[0], result[1]

        elif len(split) == 3 and split[1].isnumeric():
            time_int, time_type = split[1], split[2]
        else:
            return
    else:
        return

    if split_user:
        user = GetUserInfo(split_user) if split_user else None
        user = await user(message)

        if not user:
            return

        user_id, user_username, user_full_name = user

    user_mention = get_user_mention(user_id, user_username, user_full_name)
    admin_mention = get_user_mention(message.from_user.id, message.from_user.username, message.from_user.full_name)
    dt = get_timestamp(time_int, time_type)
    reason = args[0].split('\n', 1)[1] if len(args[0].split('\n', 1)) > 1 else 'не указана'

    if not dt:
        return await message.answer('🛑 Указано неверное время бана')

    timestamp = dt.timestamp() if dt != 'None' else None

    user_ban = await Bans.filter(
        chat_id=chat_id,
        user_id=user_id
    ).first()

    if user_ban:
        return await message.answer(f'🔴 Пользователь {user_mention} уже забанен')

    admin_rang_user = await Admins.filter(
        chat_id=chat_id,
        user_id=user_id
    ).first()

    admin_rang_admin = await Admins.filter(
        chat_id=chat_id,
        user_id=message.from_user.id
    ).first()

    user_rang = int(admin_rang_user.rang) if admin_rang_user else 0
    admin_rang = int(admin_rang_admin.rang) if admin_rang_admin else 0

    if admin_rang != 5 and admin_rang <= user_rang:
        return await message.answer(f'🔴 Вашего ранга недостаточно, чтобы исключить {user_mention}')

    try:
        (await message.bot.ban_chat_member(message.chat.id, user_id, until_date=timestamp) if timestamp else
         await message.bot.ban_chat_member(message.chat.id, user_id))
    except Exception:
        try:
            chat_user = await message.bot.get_chat_member(message.chat.id, user_id)
            if chat_user.status in ['administrator', 'creator']:
                return await message.answer(f'❌ Пользователь {user_mention} является администратором чата и не может быть ограничен.')
        except Exception:
            return await message.answer('Указан неверный ID пользователя, проверьте правильность введенных данных.')

    await Bans.create(
        chat_id=chat_id,
        user_id=user_id,
        admin_id=message.from_user.id,
        reason=reason,
        timestamp=timestamp,
        time_int=time_int,
        time_type=time_type,
        current_timestamp=datetime.now().timestamp(),
        admin_rang=admin_rang
    )

    rang_name = get_admin_name_from_rang(admin_rang)
    time = f'{time_int} {time_type}' if dt != 'None' else 'навсегда'

    await message.answer(
        f'🔴 Пользователь {user_mention} забанен\n'
        f'👤 <b>{rang_name}:</> {admin_mention}\n'
        f'💬 <b>Причина:</> {reason}\n'
        f'⏳ <b>Время:</> {time}'
    )


@rt.message(Command(
    commands=['разбан', 'вернуть'],
    html_parse_mode=True),
    F.chat.type != 'private',
)
async def unban_user(message: Message, args=None) -> None | Message:
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

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

    try:
        chat_user = await message.bot.get_chat_member(message.chat.id, user_id)
        if chat_user.status in ['administrator', 'creator', 'member']:
            return await message.answer(f'❌ Пользователь {user_mention} уже находится в чате')
    except Exception:
        return await message.answer('Указан неверный ID пользователя, проверьте правильность введенных данных')

    user_ban = await Bans.filter(
        chat_id=message.chat.id,
        user_id=user_id
    ).first()

    await message.bot.unban_chat_member(message.chat.id, user_id)

    if user_ban:
        await message.answer(f'✅ Пользователь {user_mention} разбанен.\nТеперь он снова сможет зайти в чат.')
        await user_ban.delete()
    else:
        await message.answer(f'❌ Пользователь не забанен, но я выполнил вынос из ЧС телеграмма')


@rt.message(Command(
    commands=['причина'],
    html_parse_mode=True),
    F.chat.type != 'private',
)
async def check_ban_user(message: Message, args=None):
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

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

    user_ban = await Bans.filter(
        chat_id=message.chat.id,
        user_id=user_id
    ).first()

    user_mention = get_user_mention(user_id, user_username, user_full_name)
    user_antispam = await AntiSpam.filter(
        user_id=user_id,
        activity=True
    ).first()

    if user_antispam:
        await message.answer(
            f'📛 Пользователь {user_mention} в базе АнтиСпам\n'
            f'💬 Причина: {user_antispam.reason}\n'
        )

    if not user_ban:
        return await message.answer('🛑 Пользователь не забанен')

    admin = await User.filter(id=user_ban.admin_id).first()

    admin_mention = get_user_mention(admin.id, admin.username, admin.full_name)

    if user_ban.timestamp:
        current_time = datetime.now().timestamp()
        remaining_time = max(0, int((user_ban.timestamp - current_time) // 60))
        days = remaining_time // (24 * 60)
        hours = (remaining_time % (24 * 60)) // 60
        minutes = remaining_time % 60

        text_bans = (
            f'🔴 {user_mention} забанен\n'
            f'👤 <b>Модератор:</> {admin_mention}\n'
            f'💬 <b>Причина:</> {user_ban.reason}\n'
            f'⏰ <b>До разбана:</> {days}дн. {hours}ч. {minutes}мин.'
        )
    else:
        text_bans = (
            f'🔴 {user_mention} забанен навсегда\n'
            f"👤 <b>Модератор:</> {admin_mention}\n"
            f'💬 <b>Причина:</> {user_ban.reason}'
        )
    await message.answer(text_bans)


@rt.message(Command(
    commands=['банлист', 'листбанов']),
    F.chat.type != 'private',
)
async def ban_list_chat(message: Message, args=None):
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

    await send_ban_list(message.chat.id, message, 0, user_id=message.from_user.id)


async def send_ban_list(chat_id: int, message: Message, offset: int, user_id: int, callback_query: CallbackQuery = None):

    bans = await Bans.filter(chat_id=chat_id).limit(10).offset(offset)

    text_bans = '<b>Список пользователей в банлисте:</>\n'
    if bans:
        for ban in bans:
            user = await User.get_or_none(id=ban.user_id)
            admin = await User.get_or_none(id=ban.admin_id)

            user_mention = get_user_mention(ban.user_id, user.username, user.full_name)
            admin_mention = get_user_mention(ban.admin_id, admin.username, admin.full_name)
            if ban.current_timestamp:
                data_ban = datetime.fromtimestamp(ban.current_timestamp)
                data_ban_day = data_ban.day
                data_ban_month = data_ban.month
                data_ban_year = data_ban.year
                data_str = f'{data_ban_day:02}.{data_ban_month:02}.{data_ban_year}'
            else:
                data_str = 'не известна'

            text_bans += (
                f'🔴 {user_mention}:\n'
                f'👤 <b>Модератор:</> {admin_mention}\n'
                f'💬 <b>Причина:</> {ban.reason}\n'
                f'⏰ <b>Время:</> {ban.time_int or ""} {ban.time_type}\n'
                f'📅 <b>Дата бана:</> {data_str}\n\n'
            )

        keyboard = await page_ban_list_keyboard(offset, message, user_id)

        if callback_query:
            await callback_query.message.edit_text(text_bans, reply_markup=keyboard.as_markup())
        else:
            await message.answer(text_bans, reply_markup=keyboard.as_markup())
    else:
        if callback_query:
            await callback_query.message.edit_text(f"{text_bans + 'Пуст.'}")
        else:
            await message.answer(f"{text_bans + 'Пуст.'}")


async def page_ban_list_keyboard(offset: int, message, user_id: int) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()

    if offset > 0:
        keyboard.button(text='⬅️ Назад', callback_data=f'banlist_{offset - 10}_{user_id}')

    bans = await Bans.filter(chat_id=message.chat.id).limit(1).offset(offset + 10)

    if len(bans) > 0:
        keyboard.button(text='Вперед ➡️', callback_data=f'banlist_{offset + 10}_{user_id}')
    return keyboard


@rt.callback_query(F.data.startswith('banlist_'))
async def handle_banlist_pagination(call: CallbackQuery):
    user_id = int(call.data.split('_')[2])

    if user_id != call.from_user.id:
        return await call.answer('Эта кнопочка не для вас!')

    offset = int(call.data.split('_')[1])
    await send_ban_list(call.message.chat.id, call.message, offset, user_id=user_id, callback_query=call)
    await call.answer()
