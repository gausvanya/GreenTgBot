from aiogram.types import Message
from aiogram import Router, F

from ..DataBase.Models import Rules
from ..Filters import Command #, IsAdminFilter

rt = Router()


@rt.message(Command(
    commands=['+правила'],
    html_parse_mode=True),
    F.chat.type != 'private'
)
async def set_rules_chat_handler(message: Message, args=None) -> None | Message:
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return

    split = args[0].split('\n', 1)

    if len(split[0].split()) > 1 or len(split) < 2:
        return await message.answer(
            '❗️ Используйте команду правильно\n'
            '<code>+правила\nТекст с новой строки</>'
        )

    rules_text = split[1]

    await Rules.update_or_create(
        defaults={
            'text': rules_text
        },
        chat_id=message.chat.id
    )

    await message.answer('📝 Правила чата успешно обновлены')


@rt.message(Command(
    commands=['-правила']),
    F.chat.type != 'private'
)
async def remove_rules_chat_handler(message: Message, args=None) -> None:
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return


    if len(args[0].split('\n', 1)[0].split()) > 1:
        return

    result = await Rules.filter(chat_id=message.chat.id).first()

    if result:
        await result.delete()

    await message.answer('📝 Правила чата успешно удалены')


@rt.message(Command(
    commands=['правила']),
    F.chat.type != 'private'
)
async def get_rules_chat_handler(message: Message, args=None) -> None:
    #check_admin = IsAdminFilter(args[1])
    #if not await check_admin(message):
    #    return


    if len(args[0].split('\n', 1)[0].split()) > 1:
        return

    result = await Rules.filter(chat_id=message.chat.id).first()

    if result:
        await message.answer(f'📋 Правила чата:\n{result.text}')
    else:
        await message.answer('📝 Правила чата не установлены')
