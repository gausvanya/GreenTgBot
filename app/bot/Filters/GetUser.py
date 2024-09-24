import re

from aiogram.types import Message

from ..DataBase.Models import User
from ..lib.UserBot import get_user_info


class GetUserInfo:
    def __init__(self, user: str | int):
        self.user = user
        self.user_info = None


    @staticmethod
    def clean_user_input(user: str) -> str:
        cleaned_user = re.sub(r'@|https?://t\.me/|t.me/|tg://openmessage\?user_id=|tg://user\?id=|<a href="tg://user\?id=|">.*', '', user)
        return cleaned_user.strip()

    async def __call__(self, message: Message):
        user = self.clean_user_input(str(self.user)).lower()

        if user:
            if user.isdigit():
                self.user_info = await User.filter(id=user).first()
            else:
                self.user_info = await User.filter(username=user).first()

            if self.user_info:
                return [self.user_info.id, self.user_info.username, self.user_info.full_name]
            else:
                self.user_info = await get_user_info(user)
                if not self.user_info:
                    await message.answer('❓ Вы указали неверный идентификатор пользователя или мне ничего не известно о нем')
                    return False

                await User.update_or_create(
                    id=self.user_info[0],
                    username=self.user_info[1],
                    full_name=self.user_info[2]
                )
                return self.user_info

    def __getitem__(self, index):
        if self.user_info:
            return self.user_info[0][index]
