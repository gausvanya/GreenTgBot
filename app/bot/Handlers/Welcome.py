from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION
from aiogram.types import Message, ChatMemberUpdated
from aiogram import Router, F

from ..DataBase.Models import Welcome, User
from ..Filters import Command, GetUserInfo  # , IsAdminFilter
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
        '📝 <a href="https://teletype.in/@support_bot/suuportcommands">Мой список команд</> \n'
        '📣 <a href="https://t.me/chann_support">Официальный канал</>',
        reply_markup=add_bot_administration_keyboard()
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
                             f'Добавил: {admin_mention}')
    else:
        await message.answer(f'👋 {user_mention} присоединился к чату')

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
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

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
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

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
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

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
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

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
