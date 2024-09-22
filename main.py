from app import logging_config, bot
from app.config import logging_bot_config

cfg = logging_bot_config()


def main() -> None:
    logging_config.setup(
        logging_format=cfg["LOGGING_FORMAT"],
        logging_level=cfg["LOGGING_LEVEL"]
    )

    bot.start()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Бот остановлен')
