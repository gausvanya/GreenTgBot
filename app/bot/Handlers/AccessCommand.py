from aiogram import Router, F
from aiogram.types import Message

from ..DataBase.Models import AccessCommand
from ..Filters import Command, IsAdminFilter
from ..utils import vault_access_command, get_admin_name_from_rang

rt = Router()


@rt.message(Command(
    commands=['рк'],
    html_parse_mode=True),
    F.chat.type != 'private'
)
async def set_access_command_handler(message: Message, args=None) -> None | Message:
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

    split = args[0].split('\n', 1)[0].split(maxsplit=1)[1]
    command = split[:-1].rstrip().lower()
    rang = int(split[-1])

    if vault_access_command(command) is None:
        return await message.answer('Вы указали несуществующую команду')

    await AccessCommand.update_or_create(
        defaults={'rang': rang},
        chat_id=message.chat.id,
        command=command
    )

    admin_name_rang = get_admin_name_from_rang(rang)

    await message.answer(f'🔐 Минимальный ранг команды <b>«{command}»</> изменен\n'
                         f'⚙️Новый ранг: <b>{admin_name_rang} ({rang})</>')
