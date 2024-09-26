from aiogram.types import Message
from aiogram import Router

from ..Filters import Command, IsAdminFilter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..lib.wiki_api import WikiAPI, WikiArticleResponse

rt = Router()


@rt.message(Command(commands=['wiki', 'вики']))
async def wiki_request_handler(message: Message, wiki_api: 'WikiAPI', args=None) -> None | Message:
    check_admin = IsAdminFilter(args[1])
    if not await check_admin(message):
        return

    if len(args[0].split()) < 2:
        return await message.reply('📋 Укажите свой запрос')

    wiki_query = args[0].split(maxsplit=1)[1]
    wiki_response: 'WikiArticleResponse' = await wiki_api.get_article(wiki_query)

    print(wiki_response)
    if not wiki_response:
        return await message.answer('Ошибка получения запроса\n'
                                    'Попробуйте еще раз позже')

    title = wiki_response.title
    summary = wiki_response.summary
    wiki_url = wiki_response.article_url
    photo_url = wiki_response.photo_url

    if photo_url is None:
        await message.answer(f'📝 <b>{title}</>\n\n{summary}\n\n'
                             f'↪️ <a href="{wiki_url}">Узнать подробнее</>')
    else:
        await message.answer_photo(photo_url, f'📝 <b>{title}</>\n\n{summary}\n\n'
                             f'↪️ <a href="{wiki_url}">Узнать подробнее</>')
