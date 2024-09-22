from aiogram import Router

from ..Middlewares.AntiRaidMiddlewares import AntiRaidMiddleware
from ..Middlewares.user_middleware import UserMiddleware
from ..Middlewares.statistic_middleware import StatisticMiddleware
from . import (
    handler_rules, handler_welcome, handler_ping_bot, handler_wiki, handler_fact, handler_user_id, handler_notes, handler_start,
    handler_message_pin, handler_agents, handler_kick, handler_chat_admins, handler_antispam, handler_ban, handler_mute,
    handler_profile, handler_access_command
)

root_router = Router()

root_router.message.outer_middleware(UserMiddleware())
root_router.message.outer_middleware(StatisticMiddleware())
root_router.message.outer_middleware(AntiRaidMiddleware())
root_router.include_routers(
    handler_rules.rt, handler_welcome.rt, handler_ping_bot.rt, handler_wiki.rt, handler_fact.rt, handler_user_id.rt,
    handler_start.rt, handler_notes.rt, handler_message_pin.rt, handler_kick.rt, handler_agents.rt, handler_chat_admins.rt,
    handler_mute.rt, handler_ban.rt, handler_antispam.rt, handler_profile.rt, handler_access_command.rt
)