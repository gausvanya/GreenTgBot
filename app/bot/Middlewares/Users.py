from aiogram.types import Message, TelegramObject
from aiogram import BaseMiddleware

from typing import Callable, Awaitable, Any, Dict

from pyexpat.errors import messages

from ..DataBase.Models import User, Ignore


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user = event.from_user

        await User.update_or_create(
            defaults={
                'username': user.username.lower() if user.username else None,
                'full_name': user.full_name
            },
            id=user.id
        )

        result = await Ignore.get_or_none(
            user_id=event.from_user.id,
            activity=True
        )
        if result:
            print(event.new_chat_members)
            if not event.new_chat_members:
                return

        return await handler(event, data)
