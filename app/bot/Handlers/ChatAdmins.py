from aiogram import Router, F
from aiogram.types import Message

from ..Filters import GetUserInfo, Command #, IsAdminFilter
from ..lib.UserBot import get_user_status
from ..utils import get_user_mention, get_admin_name_from_rang, get_emoji_rang_admin
from ..DataBase.Models import User, Admins, Agents

rt = Router()


@rt.message(Command(
    commands=['+модер', '+админ', 'повысить'],
    html_parse_mode=True),
    F.chat.type != 'private'
)
async def add_moder_handler(message: Message, args=None):
    admin_id = message.from_user.id
    chat_id = message.chat.id
    agents = await Agents.filter(user_id=message.from_user.id).first()
    rang = None

    if not agents:
        #check_admin = IsAdminFilter(args[1])
        #if not await check_admin(message):
        #    return
        pass

    split = args[0].split('\n', 1)[0]

    if len(split.split()) > 2 and split.split()[1].isdigit():
        rang = int(split.split()[1])
        user = GetUserInfo(split.split(maxsplit=2)[2].rstrip())
        user = await user(message)

        if not user:
            return

        user_id, user_username, user_full_name = user

    elif len(split.split()) > 1 and not split.split()[1].isdigit():
        user = GetUserInfo(split.split(maxsplit=1)[1].rstrip())
        user = await user(message)

        if not user:
            return

        user_id, user_username, user_full_name = user

    elif message.reply_to_message:
        if len(split.split()) > 1 and split.split()[1].isdigit():
            rang = int(split.split()[1])

        reply_user = message.reply_to_message.from_user
        user_id, user_username, user_full_name = reply_user.id, reply_user.username, reply_user.full_name
    else:
        return

    user_mention = get_user_mention(user_id, user_username, user_full_name)

    get_user_admin = await Admins.filter(chat_id=chat_id, user_id=user_id).first()
    get_admin_admin = await Admins.filter(chat_id=chat_id, user_id=admin_id).first()

    if rang and rang > 5:
        rang = 5
    elif not rang:
        rang = get_user_admin.rang + 1 if get_user_admin else 1

    if agents:
        if get_user_admin:
            if get_user_admin.rang == 5:
                return await message.answer(f'🛑 Пользователь {user_mention} уже имеет максимальный ранг равный 5')

    elif get_user_admin:
        if get_user_admin.rang == 5:
            return await message.answer(f'🛑 Пользователь {user_mention} уже имеет максимальный ранг равный 5')

        if get_admin_admin is None or rang > get_admin_admin.rang or get_user_admin.rang > get_admin_admin.rang:
            return await message.answer('🛑 Вашего ранга недостаточно для повышения этого модератора')

    else:
        if not get_admin_admin or rang > get_admin_admin.rang:
            return await message.answer('🛑 Вашего ранга недостаточно для повышения этого модератора')

    await Admins.update_or_create(
        defaults={'rang': rang},
        chat_id=chat_id,
        user_id=user_id
    )

    admin_rang_name = get_admin_name_from_rang(rang)
    await message.answer(f'✅ Модератору {user_mention} повышен ранг\n'
                         f'▶️ Новый ранг: <b>{admin_rang_name} ({rang})</>')


@rt.message(Command(
    commands=['-модер', '-админ', 'понизить', 'снять'],
    html_parse_mode=True),
    F.chat.type != 'private'
)
async def remove_moder_handler(message: Message, args=None):
    admin_id = message.from_user.id
    chat_id = message.chat.id
    agents = await Agents.filter(user_id=message.from_user.id).first()

    if not agents:
        #check_admin = IsAdminFilter(args[1])
        #if not await check_admin(message):
        #    return
        pass

    split = args[0].split('\n', 1)[0]

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

    get_user_admin = await Admins.filter(chat_id=chat_id, user_id=user_id).first()
    get_admin_admin = await Admins.filter(chat_id=chat_id, user_id=admin_id).first()

    if not get_user_admin:
        return await message.answer(f'🛑 Пользователь {user_mention} не является модератором')

    if agents:
        if args[1] in ['снять', 'разжаловать']:
            await get_user_admin.delete()
            await message.answer(f'✅ Модератор {user_mention} разжалован')
        else:
            if get_user_admin.rang - 1 < 1:
                await get_user_admin.delete()
                await message.answer(f'✅ Модератор {user_mention} разжалован')
            else:
                await Admins.update_or_create(
                    defaults={'rang': get_user_admin.rang - 1},
                    chat_id=chat_id,
                    user_id=user_id
                )
                admin_rang_name = get_admin_name_from_rang(get_user_admin.rang - 1)
                await message.answer(f'✅ Ранг модератора {user_mention} понижен\n▶️ Новый ранг: <b>{admin_rang_name} ({get_user_admin.rang - 1})</>')
    else:
        if not get_admin_admin:
            return await message.answer('🛑 Вашего ранга недостаточно для понижения этого модератора')

        if args[1] in ['снять', 'разжаловать'] and get_user_admin.rang <= get_admin_admin.rang:
            if get_user_admin.rang == 5 <= get_admin_admin.rang == 5:
                await get_user_admin.delete()
                await message.answer(f'✅ Модератор {user_mention} разжалован')
            elif get_user_admin.rang < get_admin_admin.rang:
                await get_user_admin.delete()
                await message.answer(f'✅Модератор {user_mention} разжалован')
            else:
                await message.answer(f'🛑 Вашего ранга недостаточно чтобы понизить {user_mention}')

        else:
            if get_user_admin.rang == 5 <= get_admin_admin.rang == 5:
                await Admins.update_or_create(
                    defaults={'rang': 4},
                    chat_id=chat_id,
                    user_id=user_id
                )
                admin_rang_name = get_admin_name_from_rang(4)
                await message.answer(f'✅ Ранг модератора {user_mention} понижен\n▶️ Новый ранг: <b>{admin_rang_name} (4)</>')
            elif get_user_admin.rang < get_admin_admin.rang:
                if get_user_admin.rang - 1 < 1:
                    await get_user_admin.delete()
                    rang = get_user_admin.rang - 1
                    admin_rang_name = get_admin_name_from_rang(rang)
                    await message.answer(f'✅ Ранг модератора {user_mention} понижен\n▶️ Новый ранг: <b>{admin_rang_name} ({rang})</>')
                else:
                    await Admins.update_or_create(
                        defaults={'rang': get_user_admin.rang - 1},
                        chat_id=chat_id,
                        user_id=user_id
                    )
                    await message.answer(f'✅ Модератор {user_mention} разжалован')
            else:
                await message.answer(f'🛑 Вашего ранга недостаточно чтобы понизить {user_mention}')


@rt.message(Command(commands=['кто админ', 'админы', 'модеры']), F.chat.type != 'private')
async def chat_moder_list_handler(message: Message, args=None):
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

    admins = await Admins.filter(chat_id=message.chat.id).all()

    if not admins:
        return await message.answer('В чате царит анархия')

    ranked_admins = {i: [] for i in range(1, 6)}

    for admin in admins:
        user_id = admin.user_id
        rang = admin.rang
        user = await User.filter(id=user_id).first()
        user_mention = get_user_mention(user_id, user.username, user.full_name)

        user_status = await get_user_status(user.username if user.username else user.id)
        user_status_emoji = '🎾' if user_status == 'онлайн' else '🏐'

        ranked_admins[rang].append((user_mention, user_status_emoji))

    text = '<b>📝 Список модераторов чата:</>\n'

    for rang in range(5, 0, -1):
        if ranked_admins[rang]:
            emoji_rang = get_emoji_rang_admin(rang)
            admin_rang_name = get_admin_name_from_rang(rang)
            text += f'\n{emoji_rang} <b>{admin_rang_name}</>:\n'
            text += '\n'.join(f'{status_emoji} {mention}' for mention, status_emoji in ranked_admins[rang]) + '\n'

    await message.answer(text)



@rt.message(Command(
    commands=['восстановить права', 'восстановить админку']),
    F.chat.type != 'private'
)
async def restore_tg_admin(message: Message) -> None:
    chat_member = await message.bot.get_chat_member(
        chat_id=message.chat.id,
        user_id=message.from_user.id
    )

    if chat_member.status == 'creator':
        await Admins.update_or_create(
            defaults={'rang': 5},
            chat_id=message.chat.id,
            user_id=message.from_user.id
        )
        await message.answer('✅ Права создателя восстановлены')
    else:
        await message.answer('🛑 Вы не являетесь создателем чата')