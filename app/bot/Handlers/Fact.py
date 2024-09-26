from aiogram.types import Message
from aiogram import Router

from deep_translator import GoogleTranslator
import randfacts

from ..Filters import Command, IsAdminFilter

rt = Router()


@rt.message(Command(commands=['факт']))
async def get_random_fact_handler(message: Message, args=None) -> None:
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

    if len(args[0].split('\n', 1)[0].split()) > 1:
        return

    fact = randfacts.get_fact(filter_enabled=True)
    translated_fact = GoogleTranslator(source='auto', target='ru').translate(fact)
    await message.answer(f'🤔 <b>Интересный факт:</>\n'
                         f'{translated_fact}')
