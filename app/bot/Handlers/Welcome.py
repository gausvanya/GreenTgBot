from datetime import datetime

from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION, IS_MEMBER, IS_ADMIN
from aiogram.types import Message, ChatMemberUpdated
from aiogram import Router, F

from ..DataBase.Models import Welcome, User, AntiSpam, Statistic, Admins, ChatSettings
from ..Filters import Command, GetUserInfo , IsAdminFilter
from ..KeyBoards import add_bot_administration_keyboard
from ..utils import get_user_mention

rt = Router()


@rt.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def add_bot_in_chat_handler(message: ChatMemberUpdated) -> None:
    await message.answer(
        f'<b>👋 Приветствую, {message.chat.full_name}!</>\nℹ️'
        'Выдать права администратора мне можно по кнопке ниже или по гайду:\n'
        'Переходим в настройки чата -> переходим в раздел «Администраторы» -> нажимаете «Добавить администратора» -> '
        'ищите в участниках бота -> кликаете на него -> выдаёте <b>ВСЕ</> права кроме анонимности.\n\n'
        '📝 <a href="https://teletype.in/">Мой список команд</> \n'
        '📣 <a href="https://t.me/">Официальный канал</>',
        reply_markup=add_bot_administration_keyboard()
    )
    await registration_user_chat(message)


@rt.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_ADMIN))
async def set_administrator_chat_bot_handler(message: ChatMemberUpdated) -> None:
    print('aadefe')
    result = await Admins.filter(user_id=message.from_user.id).first()
    if result is None:
        await Admins.create(user_id=message.from_user.id, chat_id=message.chat.id, rang=5)

    result = await ChatSettings.filter(chat_id=message.chat.id).first()
    print(result)
    if result is None:
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        await ChatSettings.create(
            chat_id=message.chat.id,
            default_time_ban='навсегда',
            default_time_mute = '1_час',
            default_time_warn = '7_дней',
            default_limit_warn = '3',
            default_result_warn = 'бан_навсегда'
        )


async def check_antispam_status(message: ChatMemberUpdated) -> bool:
    user = message.new_chat_member.user
    user_mention = get_user_mention(user.id, user.username, user.full_name)

    result = await AntiSpam.filter(
        user_id=user.id,
        activity=True
    ).first()

    if result:
        get_chat_member = await message.bot.get_chat_member(message.chat.id, message.from_user.user.id)

        if get_chat_member.status in ('creator', 'administrator'):
            await message.answer(
                '📛 Внимание!\n'
                f'Вы пригласили {user_mention} в чат\n'
                'Он находится в базе АнтиСпам\n'
                f'💬 Причина: {result.reason}'
            )
            return True
        else:
            await message.bot.ban_chat_member(message.chat.id, user.id)
            try:
                await message.bot.send_message(chat_id=user.id,
                                               text='📛  Ваша заявка на вступление в чат отклонена\n'
                                                    'Вы находитесь в базе АнтиСпам бота\n'
                                                    f'💬 Причина: {result.reason}\n\n'
                                                    f'Во всем вопросам в чат тех-поддержи')
            except:
                pass

            await message.answer(
                '📛 Внимание!\n'
                f'Пользователь {user_mention} находится в базе АнтиСпам\n'
                f'💬 Причина: {result.reason}\n'
                '➖ Исключаю...'
            )
        return False


async def registration_user_chat(message: ChatMemberUpdated):
    user = message.new_chat_member.user

    result = await Statistic.filter(
        chat_id=message.chat.id,
        user_id=user.id
    ).first()

    if not result:
        date = datetime.now().strftime('%d.%m.%Y')
        await Statistic.create(
            chat_id=message.chat.id,
            user_id=user.id,
            count=0,
            date=date
        )


@rt.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def join_chat_member_handler(message: ChatMemberUpdated) -> None | Message:
    chat_id = message.chat.id
    user = message.new_chat_member.user
    admin = message.from_user
    user_id, user_username, user_full_name = user.id, (user.username.lower() if user.username else None), user.full_name
    admin_id, admin_username, admin_full_name = admin.id, admin.username, admin.full_name

    await User.update_or_create(
        defaults={
            'username': user_username,
            'full_name': user_full_name
        },
        id=user_id
    )

    user_mention = get_user_mention(user_id, user_username, user_full_name)
    admin_mention = get_user_mention(admin_id, admin_username, admin_full_name)

    if user_id != admin_id:
        await message.answer(f'👋 {user_mention} присоединился к чату\n'
                             f'➕ Добавил: {admin_mention}')
    else:
        await message.answer(f'👋 {user_mention} присоединился к чату')

    antispam = await check_antispam_status(message)
    if antispam:
        return

    await registration_user_chat(message)

    result = await Welcome.filter(
        chat_id=chat_id
    ).first()

    if not result:
        return

    welcome_text = result.text.replace('{имя}', user_mention)
    photo_id = result.photo_id

    if photo_id:
        await message.answer_photo(photo=photo_id, caption=f'👋 <b>Приветствие:</>\n{welcome_text}')
    else:
        await message.answer(f'👋 <b>Приветствие:</>\n{welcome_text}')


@rt.chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def leave_chat_member_handler(message: ChatMemberUpdated) -> None:
    user = message.old_chat_member.user
    admin = message.from_user
    user_mention = get_user_mention(user.id, user.username, user.full_name)
    admin_mention = get_user_mention(admin.id, admin.username, admin.full_name)

    if admin.id != user.id:
        await message.answer(f'🛑 Пользователь {user_mention} исключен\n'
                             f'👤 Администратор: {admin_mention}')
    else:
        await message.answer(f'👋 Пользователь {user_mention} покинул чат')


@rt.message(Command(
    commands=['+приветствие'],
    html_parse_mode=True),
    F.chat.type != 'private',
)
async def set_welcome_chat_handler(message: Message, args=None) -> None | Message:
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

    split = args[0].split('\n', 1)

    if len(split[0].split()) > 1 or len(split) < 2:
        return await message.answer(
            '❗️ Используйте команду правильно\n'
            '<code>+приветствие\nТекст с новой строки</>'
        )

    welcome_text = split[1]
    photo_id = message.photo[-1].file_id if message.photo else None

    await Welcome.update_or_create(
        defaults={
            'text': welcome_text,
            'photo_id': photo_id
        },
        chat_id=message.chat.id
    )

    await message.answer('✅ Приветствие новых пользователей установлено')


@rt.message(Command(
    commands=['-приветствие']),
    F.chat.type != 'private',
)
async def remove_chat_welcome_handler(message: Message, args=None) -> None:
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

    if len( args[0].split('\n', 1)[0].split()) > 1:
        return

    result = await Welcome.filter(chat_id=message.chat.id).first()

    if result:
        await result.delete()

    await message.answer('✅ Приветствие новых пользователей удалено')


@rt.message(Command(
    commands=['приветствие'],),
    F.chat.type != 'private',
)
async def get_chat_welcome_handler(message: Message, args=None) -> None | Message:
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

    split = args[0].split('\n', 1)

    if len(split[0].split()) > 1:
        return

    result = await Welcome.filter(chat_id=message.chat.id).first()

    if not result:
        return await message.answer('🛑 Приветствие чата еще не установлено')

    welcome_text = result.text
    photo_id = result.photo_id

    if photo_id:
        await message.answer_photo(photo=photo_id, caption=f'👋 <b>Приветствие:</>\n{welcome_text}')
    else:
        await message.answer(f'👋 <b>Приветствие:</>\n{welcome_text}')


@rt.message(Command(
    commands=['поприветствуй'],
    html_parse_mode=True),
)
async def command_welcome_user_handler(message: Message, args=None) -> None | Message:
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

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

    result = await Welcome.filter(chat_id=message.chat.id).first()

    if not result:
        return await message.answer('🛑 Приветствие чата не установлено')

    welcome_text = result.text.replace('{имя}', user_mention)
    photo_id = result.photo_id

    if photo_id:
        await message.answer_photo(photo=photo_id, caption=f'👋 <b>Приветствие:</>\n{welcome_text}')
    else:
        await message.answer(f'👋 <b>Приветствие:</>\n{welcome_text}')
