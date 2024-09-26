from aiogram.types import Message, TelegramObject
from aiogram import BaseMiddleware

from typing import Callable, Awaitable, Any, Dict

from ..Filters import MessageFilter


class MessageFilters(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        check_filters = MessageFilter()
        a = await check_filters(event)
        print(a)

        return await handler(event, data)



