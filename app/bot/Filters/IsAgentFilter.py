from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.bot.DataBase.Models import Agents


class IsAgentFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        result = await Agents.get_or_none(user_id=message.from_user.id)

        if result:
            return True
        return False
