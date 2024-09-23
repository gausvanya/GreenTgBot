from aiogram import Router

from . import (
    Start, Notes, Rules, Fact, Welcome, BotPing, Wiki, UserId, Kick
)

root_router = Router()

root_router.include_routers(
    Start.rt, Notes.rt, Rules.rt, Fact.rt, Welcome.rt, BotPing.rt, Wiki.rt, UserId.rt, Kick.rt
)
