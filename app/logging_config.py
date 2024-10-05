import logging
from typing import Union

from app.bot.utils import InterceptHandler


def setup(logging_level: Union[str, int] = 'DEBUG'):
    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=logging.getLevelName(logging_level)
    )
