from aiogram import Router

from . import (Start)

root_router = Router()

root_router.include_routers(Start.rt)