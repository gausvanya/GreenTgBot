from aiogram.types import Message
from aiogram import Router, F

from ..Filters import Command #, IsAdminFilter

rt = Router()


@rt.message(Command(
    commands=['пин', 'закреп']),
    F.chat.type != 'private'
)
async def pin_message_handler(message: Message, args=None) -> None | Message:
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

    if len(args[0].split('\n', 1)[0].split()) > 1:
        return

    if not message.reply_to_message:
        return await message.answer('⛔️ Команда должна быть вызвана в ответ на смс')

    message_url = f'https://t.me/c/{str(message.chat.id)[4:]}/{message.reply_to_message.message_id}'

    await message.reply_to_message.pin()
    await message.answer(f'✅ <a href="{message_url}">Сообщение</> закреплено')


@rt.message(Command(
    commands=['анпин', 'откреп', '-пин']),
    F.chat.type != 'private',
)
async def unpin_message_handler(message: Message, args=None):
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

    if len(args[0].split('\n', 1)[0].split()) > 1:
        return

    if not message.reply_to_message:
        return await message.answer('⛔️ Команда должна быть вызвана в ответ на смс')

    message_url = f'https://t.me/c/{str(message.chat.id)[4:]}/{message.reply_to_message.message_id}'
    await message.reply_to_message.unpin()
    await message.answer(f'✅ <a href="{message_url}">Сообщение</> откреплено')
