from aiogram.types import Message, TelegramObject
from aiogram import BaseMiddleware

from typing import Callable, Awaitable, Any, Dict
from datetime import datetime

from app.bot.DataBase.Models import Statistic


class StatisticMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        date = datetime.now().strftime('%d.%m.%Y')

        result = await Statistic.filter(
            chat_id=event.chat.id,
            user_id=event.from_user.id,
            date=date
        ).first()

        count = result.count if result else 0

        await Statistic.update_or_create(
            defaults={'count': count + 1},
            chat_id=event.chat.id,
            user_id=event.from_user.id,
            date=date
        )

        return await handler(event, data)
