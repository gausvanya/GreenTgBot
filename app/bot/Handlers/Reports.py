from aiogram.types import Message
from aiogram import Router, F
from aiogram.types import CallbackQuery

from ..DataBase.Models import Admins, Report, ReportBinding
from ..Filters import GetUserInfo, Command #, IsAdminFilter
from ..KeyBoards import report_chat_keyboard, report_admin_keyboard
from ..utils import get_user_mention

rt = Router()


@rt.message(Command(
    commands=['репорт', 'report', 'жалоба'],
    html_parse_mode=True),
    F.chat.type != 'private',
)
async def report_user_handler(message: Message, args=None) -> None | Message:
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

    admin = message.from_user
    user_mention = get_user_mention(user_id, user_username, user_full_name)
    admin_mention = get_user_mention(admin.id, admin.username, admin.full_name)
    reason = args[0].split('\n', 1)[1] if len(args[0].split('\n', 1)) > 1 else 'не указана'

    admin_chat_id = await ReportBinding.filter(chat_id=message.chat.id).first()
    if not admin_chat_id:
        return await message.answer('❌ Чат не привязан к админ чату для отправки жалоб')

    admin_chat_id = admin_chat_id.admin_chat_id

    admins = await Admins.filter(chat_id=message.chat.id, user_id=user_id).first()

    if user_id == message.from_user.id:
        return await message.answer('тютю?')

    if admins or message.bot.id == user_id:
        return await message.answer('👑 Против власти не попрешь!')

    chat_message_id = await message.answer(
        f'✅ <b>Жалоба на {user_mention} (<code>@{user_id}</>) отправлена модерации</>\n'
        '❤️ Спасибо за помощь ❤️',
        reply_markup=report_chat_keyboard(  )
    )

    message_link = f"https://t.me/c/{str(message.chat.id)[4:]}/{chat_message_id.message_id}"

    admin_message_id = await message.bot.send_message(
        admin_chat_id,
        f'📛 <b>Поступила новая жалоба</>\n\n'
        f'👤 <b>Жалоба на:</> {user_mention} (<code>@{user_id}</>)\n'
        f'👥 <b>Пожаловался:</> {admin_mention} (<code>@{admin.id}</>)\n'
        f'💬 <b>Причина:</> {reason}',
        reply_markup=report_admin_keyboard(message.chat.id, user_id, message_link)
    )

    await Report.create(
        chat_id=message.chat.id,
        user_id=user_id,
        admin_id=admin.id,
        reason=reason,
        chat_message_id=chat_message_id.message_id,
        admin_chat_id=admin_chat_id,
        admin_message_id=admin_message_id.message_id
    )


@rt.message(Command(
    commands=['идчата', 'чатид']),
    F.chat.type != 'private',
)
async def get_chat_id_handler(message: Message, args=None):
    if len(args[0].split('\n', 1)[0].split()) > 1:
        return

    await message.answer(f'🆔 этого чата: <code>{message.chat.id}</>')


@rt.message(Command(
    commands=['привязать репорты']),
    F.chat.type != 'private',
)
async def report_binding_handler(message: Message, args=None):
    split = args[0].split('\n', 1)[0].split()

    if len(split) > 3 and not split[2].isdigit():
        return

    chat_id = split[2]
    get_chat = await message.bot.get_chat(chat_id)

    if get_chat.username:
        chat_mention =  f'<a href="https://t.me/{get_chat.username}">{get_chat.full_name}</>'
    else:
        chat_mention =  f'<a href="https://t.me/c/{chat_id[4:]}">{get_chat.full_name}</>'

    await ReportBinding.update_or_create(
        defaults={'chat_id': int(chat_id)},
        admin_chat_id=message.chat.id
    )

    await message.answer(f'✅ Чат {chat_mention} привязан к этому Админ-Чату\n'
                         f'Теперь все жалобы из него будут приходить сюда')


@rt.message(Command(
    commands=['отвязать репорты']),
    F.chat.type != 'private',
)
async def report_unbinding_handler(message: Message, args=None):
    split = args[0].split('\n', 1)[0].split()

    if len(split) > 3 and not split[2].isdigit():
        return

    chat_id = split[2]
    get_chat = await message.bot.get_chat(chat_id)

    if get_chat.username:
        chat_mention =  f'<a href="https://t.me/{get_chat.username}">{get_chat.full_name}</>'
    else:
        chat_mention =  f'<a href="https://t.me/c/{chat_id[4:]}">{get_chat.full_name}</>'

    result = await ReportBinding.filter(chat_id=int(chat_id), admin_chat_id=message.chat.id).first()
    if not result:
        return await message.answer(f'Чат {chat_mention} не привязан')

    await result.delete()
    await message.answer(f'✅ Чат {chat_mention} отвязан от этого Админ-Чата\n'
                         f'Теперь все жалобы из него будут приходить сюда')


@rt.callback_query(F.data == 'delete_report_chat')
async def delete_report_chat(call: CallbackQuery):
    result = await Report.filter(
        chat_id=call.message.chat.id,
        chat_message_id=call.message.message_id
    ).first()

    admins = await Admins.filter(chat_id=call.message.chat.id, user_id=call.from_user.id).first()

    if not admins:
        return await call.answer('🔐 У вас недостаточно прав для удаления жалобы')

    if not result:
        return await call.answer('❌ Жалоба не найдена в базе данных, возможно ее уже удалили')

    admin_chat_id = result.admin_chat_id
    admin_message_id = result.admin_message_id

    try:
        await call.message.delete()
        await call.bot.delete_message(admin_chat_id, admin_message_id)
    except Exception as e:
        await call.answer(f'Произошла ошибка при попытке удалить сообщение: {e}')

    await result.delete()


@rt.callback_query(F.data == 'delete_report_admin')
async def delete_report_admin_chat(call: CallbackQuery):
    result = await Report.filter(
        admin_chat_id=call.message.chat.id,
        admin_message_id=call.message.message_id
    ).first()

    admins = await Admins.filter(chat_id=call.message.chat.id, user_id=call.from_user.id).first()

    if not admins:
        return await call.answer('🔐 У вас недостаточно прав для удаления жалобы')

    if not result:
        return await call.answer('❌ Жалоба не найдена в базе данных, возможно ее уже удалили')

    chat_id = result.chat_id
    chat_message_id = result.chat_message_id

    try:
        await call.message.delete()
        await call.bot.delete_message(chat_id, chat_message_id)
    except Exception as e:
        await call.answer(f'Произошла ошибка при попытке удалить сообщение: {e}')

    await result.delete()


@rt.callback_query(F.data.startswith('ban_user_'))
async def report_ban_user(call: CallbackQuery):
    await call.answer('функция пока не доступна')








