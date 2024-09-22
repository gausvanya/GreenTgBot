from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router, F

from ..KeyBoards import bot_add_to_chat_keyboard
from ..utils import get_user_mention

rt = Router()


@rt.message(CommandStart(ignore_case=True), F.chat.type == 'private')
async def start_command_handler(message: Message) -> None:
    split = message.html_text.split('\n', 1)
    if len(split[0].split()) > 1:
        return

    user_mention = get_user_mention(message.from_user.id, message.from_user.username, message.from_user.full_name)

    await message.reply(
        f'👋 Приветствую, {user_mention}!\n'
        'Я создан, чтобы поддерживать порядок и гармонию в ваших чатах\n\n'
        '⚖️ Мы хотим чтобы наш бот был для вас полезен, так что идеи для развития вы можете '
        'предложить в нашем <a href="https://t.me/UpGreenDayGroup">официальном чате</>, там же вы узнаете об свежих обновлениях\n\n'
        '🛠 Бот находится на стадии разработки.',
        reply_markup=bot_add_to_chat_keyboard()
    )
