from abc import ABC
import re

from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.bot.lib.UserBot import get_chat
from app.bot.utils import get_user_mention
import asyncio

MESSAGES_COUNT = {}


class MessageFilter(BaseFilter, ABC):
    def __init__(self):
        super().__init__()


    async def __call__(self, message: Message):
        text = message.text.lower() if message.text else None
        user_mention = get_user_mention(message.from_user.id, message.from_user.username, message.from_user.full_name)

        if text:
            spam = await self.telegram_spam_filter(text)
            if spam:
                await message.answer(
                    '🛑 В сообщение обнаружена ссылка на ресурсы Telegram\n'
                    f'Пользователь {user_mention} исключен из чата\n\n'
                    f'<code>бан навсегда @{message.from_user.id}\nСпам: Ссылка на ресурсы Telegram</>'
                )
                await message.delete()
                return True

            referral = await self.telegram_referral_spam_filter(text)
            if referral:
                await message.answer(
                    '🛑 В сообщение обнаружена реферальная ссылка\n'
                    f'Пользователь {user_mention} исключен из чата\n\n'
                    f'<code>бан навсегда @{message.from_user.id}\nСпам: Реферальные ссылки Telegram</>'
                )
                await message.delete()
                return True

            all_link = await self.all_links_filter(text)
            if all_link:
                await message.answer(
                    '🛑 В сообщение обнаружена ссылка\n'
                    f'Пользователь {user_mention} исключен из чата\n\n'
                    f'<code>бан навсегда @{message.from_user.id}\nСпам: Ссылки</>'
                )
                return True
        raid = await self.raid_filter(message)
        if raid:
            await message.answer(
                '🛑 Подозрительная активность похожая на рейд\n'
                f'Пользователь {user_mention} исключен из чата\n\n'
                f'<code>бан навсегда @{message.from_user.id}\nРейд</>'
            )
            await message.delete()
            return True
        return False


    @staticmethod
    async def telegram_spam_filter(text: str) -> bool:
        spam_links = re.findall(r't.me/\+[a-zA-Z0-9]+', text)

        if spam_links:
            return True

        text = text.split()
        for msg in text:
            if msg.startswith('https://t.me/') or msg.startswith('t.me/') or msg.startswith('http://t.me/'):
                username = msg.split("/")[-1]

                chat = await get_chat(username)
                if chat:
                    chat_type = chat.type.name.lower()
                    if chat_type in ['group', 'supergroup', 'channel']:
                        return True
        return False

    @staticmethod
    async def raid_filter(message: Message) -> bool:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if chat_id not in MESSAGES_COUNT:
            MESSAGES_COUNT[chat_id] = {}

        if user_id not in MESSAGES_COUNT[chat_id]:
            MESSAGES_COUNT[chat_id][user_id] = []

        MESSAGES_COUNT[chat_id][user_id].append(asyncio.get_event_loop().time())
        current_time = asyncio.get_event_loop().time()

        result = MESSAGES_COUNT[chat_id][user_id] = [
            msg_time for msg_time in MESSAGES_COUNT[chat_id][user_id] if current_time - msg_time < 8
        ]

        if len(result) >= 10:
            MESSAGES_COUNT[chat_id][user_id] = []
            return True
        return False


    @staticmethod
    async def telegram_referral_spam_filter(text: str) -> bool:
        return False


    @staticmethod
    async def all_links_filter(text: str) -> bool:
        return False


    
