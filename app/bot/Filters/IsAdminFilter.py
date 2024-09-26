from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.bot.DataBase.Models import AccessCommand, Admins
from app.bot.utils import get_admin_name_from_rang, vault_access_command


class IsAdminFilter(BaseFilter):
    def __init__(self, command: str):
        self.command = command.lower()

    async def __call__(self, message: Message) -> bool:
        result = await AccessCommand.filter(
            chat_id=message.chat.id,
            command=self.command
        ).first()

        if result:
            rang_cmd = result.rang
        else:
            rang_cmd = int(vault_access_command(self.command))

        result = await Admins.get_or_none(
            chat_id=message.chat.id,
            user_id=message.from_user.id
        )

        user_rang = result.rang if result else 0
        user_name_rang = get_admin_name_from_rang(user_rang)
        cmd_name_rang = get_admin_name_from_rang(rang_cmd)

        if rang_cmd > user_rang:
            await message.answer(f'🔓 Вашего ранга {user_name_rang} ({user_rang}) недостаточно для данной команды\n'
                                 f'🚫 Команда доступна с ранга {cmd_name_rang} ({rang_cmd})')
            return False
        return True