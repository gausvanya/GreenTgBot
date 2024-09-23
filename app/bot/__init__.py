from aiohttp import web

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.config import webhook_bot_config
from .Handlers import root_router
from .lib.wiki_api import WikiAPI


router = Router()
cfg = webhook_bot_config()


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{cfg['BASE_WEBHOOK_URL']}{cfg['WEBHOOK_PATH']}", secret_token=cfg['WEBHOOK_SECRET'],
                          allowed_updates=['message', 'callback_query', 'my_chat_member', 'chat_member'])


def start() -> None:
    dp = Dispatcher()
    dp['wiki_api'] = WikiAPI()
    dp.include_router(router)
    dp.startup.register(on_startup)
    bot = Bot(token=cfg['BOT_TOKEN'], default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True))
    dp.include_router(root_router)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=cfg['WEBHOOK_SECRET'],
    )
    webhook_requests_handler.register(app, path=cfg['WEBHOOK_PATH'])
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=cfg['WEB_SERVER_HOST'], port=int(cfg['WEB_SERVER_PORT']))
