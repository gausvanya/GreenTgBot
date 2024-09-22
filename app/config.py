from dotenv import load_dotenv
import os

load_dotenv()
env = os.environ


# LOAD BOT SETTINGS
def webhook_bot_config():
    return {
        "BOT_TOKEN": env['BOT_TOKEN'],
        "WEB_SERVER_HOST": env["WEB_SERVER_HOST"],
        "WEB_SERVER_PORT": env['WEB_SERVER_PORT'],
        "WEBHOOK_PATH": env['WEBHOOK_PATH'],
        "WEBHOOK_SECRET": env['WEBHOOK_SECRET'],
        "BASE_WEBHOOK_URL": env['BASE_WEBHOOK_URL'],
    }


# LOAD LOGGING SETTINGS
def logging_bot_config():
    return {
        "LOGGING_LEVEL": env["LOGGING_LEVEL"],
        "LOGGING_FORMAT": env["LOGGING_FORMAT"]
    }
