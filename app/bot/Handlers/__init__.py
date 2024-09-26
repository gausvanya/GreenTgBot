from aiogram import Router

from . import (
    Start, Notes, Rules, Fact, Welcome, BotPing, Wiki, UserId, Kick, MessagePin, ChatAdmins, Agents, Reports, AntiSpamBase,
    ProfileUser, AccessCommand, Ban
)
from ..Middlewares.MessageFilters import MessageFilters
from ..Middlewares.Users import UserMiddleware
from ..Middlewares.Statistic import StatisticMiddleware


root_router = Router()

root_router.message.outer_middleware(UserMiddleware())
root_router.message.outer_middleware(MessageFilters())
root_router.message.outer_middleware(StatisticMiddleware())
root_router.include_routers(
    Start.rt, Notes.rt, Rules.rt, Fact.rt, Welcome.rt, BotPing.rt, Wiki.rt, UserId.rt, Kick.rt, MessagePin.rt,
    ChatAdmins.rt, Agents.rt, Reports.rt, Ban.rt, AntiSpamBase.rt, ProfileUser.rt, AccessCommand.rt
)
