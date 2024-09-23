from aiogram.types import Message
from aiogram import Router, F

from ..utils import get_user_mention, get_admin_name_from_rang, get_emoji_rang_admin
from ..DataBase.Models import Agents, Statistic, Admins
from ..Filters import GetUserInfo, Command #, IsAdminFilter
from ..lib.UserBot import get_user_status

from datetime import datetime, timedelta

rt = Router()


@rt.message(Command(
    commands=['профиль', 'мой профиль', 'кто я', 'кто ты'],
    html_parse_mode=True),
    F.chat.type != 'private'
)
async def profile_user(message: Message, args=None) -> None | Message:
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

    split = args[0].split('\n', 1)[0].lower()
    user = None

    if split in ['мой профиль', 'кто я'] or split == 'профиль' and len(split.split()) == 1:
        user = message.from_user
        user_id, user_username, user_full_name = user.id, user.username, user.full_name
        profile_photo = await message.from_user.get_profile_photos(limit=1)
        is_bot = message.from_user.is_bot
    else:
        if split.startswith('кто ты') and len(split.split()) > 2:
            user = GetUserInfo(split.split(maxsplit=2)[2].rstrip())

        elif split.startswith('профиль') and len(split.split()) > 1:
            user = GetUserInfo(args[0].split('\n', 1)[0].split(maxsplit=1)[1].rstrip())

        elif message.reply_to_message:
            reply_user = message.reply_to_message.from_user
            user_id, user_username, user_full_name = reply_user.id, reply_user.username, reply_user.full_name
            profile_photo = await reply_user.get_profile_photos(limit=1)
            is_bot = reply_user.is_bot
        else:
            return

        if user:
            user = await user(message)
            if not user:
                return

            user_id, user_username, user_full_name = user
            profile_photo = await message.bot.get_user_profile_photos(limit=1, user_id=user_id)
            is_bot = (await message.bot.get_chat_member(message.chat.id, user_id)).user.is_bot

    user_mention = get_user_mention(user_id, user_username, user_full_name)
    chat_member = await message.bot.get_chat_member(message.chat.id, user_id)
    agent = await Agents.get_or_none(user_id=user_id)

    get_status = await get_user_status(user_username if user_username else user_id, return_date_str=True)

    if agent:
        user_status = 'агент бота'
    elif chat_member.status == 'creator':
        user_status = 'создатель чата'
    elif chat_member.status == 'administrator':
        user_status = 'администратор'
    elif chat_member.status == 'member':
        user_status = 'участник'
    elif chat_member.status in ['left', 'kicked']:
        user_status = 'бывший участник'
    else:
        user_status = 'Пользователь не найден'

    type_user = 'бот' if is_bot else 'пользователь'

    statistic = await Statistic.filter(
        chat_id=message.chat.id,
        user_id=user_id,
    ).all()

    if statistic:
        day_stat = 0
        for stat in statistic:
            if stat.date == datetime.now().strftime('%d.%m.%Y'):
                day_stat = stat.count

        week_stat = sum(stat.count for stat in statistic if
                        datetime.strptime(str(stat.date), '%d.%m.%Y') >= datetime.now() - timedelta(days=7))
        month_stat = sum(stat.count for stat in statistic if
                         datetime.strptime(stat.date, '%d.%m.%Y') >= datetime.now() - timedelta(days=30))
        total_stat = sum(stat.count for stat in statistic)

        first_appearance = await Statistic.filter(
            chat_id=message.chat.id,
            user_id=user_id
        ).order_by('date').values('date')
    else:
        return await message.answer('Пользователь раньше не заходил в чат')

    result = await Admins.filter(
        chat_id=message.chat.id,
        user_id=user_id
    ).first()

    rang = result.rang if result else 0
    admin_rang_name = get_admin_name_from_rang(rang)
    emoji_rang = get_emoji_rang_admin(rang)

    text = (
        f'👤 Это {type_user} {user_mention}, {user_status}\n\n'
        f'{emoji_rang} ранг: {admin_rang_name}\n'
        f'▶️ Тг-статус: {get_status}\n'
        f'🕰 Первое появление: {first_appearance[0]["date"]}\n'
        f'⚡️ Статистика(дн | нед | мес | всего): {day_stat} | {week_stat} | {month_stat} | {total_stat}'
    )

    if profile_photo.photos:
        photo = profile_photo.photos[0][-1].file_id
        await message.answer_photo(
            photo=photo,
            caption=text
        )
    else:
        await message.answer(text)
