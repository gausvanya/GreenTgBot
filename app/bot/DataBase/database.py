import logging
import os

from tortoise import Tortoise


async def db_start() -> None:
    db_path = os.path.abspath('app/bot/DataBase/db.sqlite3')
    db_url = f'sqlite:///{db_path}'

    await Tortoise.init(
        db_url=db_url,
        modules = {
            'models': [
            'app.bot.DataBase.Models'
            ]
        }
    )

    await Tortoise.generate_schemas()
    logging.info('Соединение с БД установлено')


async def db_close() -> None:
    await Tortoise.close_connections()
    logging.info('Соединение с БД разорвано')

