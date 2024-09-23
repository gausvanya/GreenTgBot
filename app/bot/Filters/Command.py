import re
from typing import Union, List

from aiogram.filters import BaseFilter
from aiogram.types import Message


class Command(BaseFilter):
    def __init__(self, commands: Union[list[str], str], prefixes: List[str] = None, html_parse_mode: bool = False):
        self.commands = commands
        self.html_parse_mode = html_parse_mode
        self.prefixes = prefixes if prefixes is not None else ['сап ', '.', '. ', '!', '! ', '/', '/ ', '']

    async def __call__(self, message: Message):
        if message.text is None and message.caption is None:
            return

        def get_msg_text_with_parse_mode():
            if self.html_parse_mode is True:
                return message.html_text or ''
            return message.text or ''

        def check_command_args(pattern, text):
            match = re.match(pattern, text)
            if match:
                return match.groups()
            return False

        msg_text = get_msg_text_with_parse_mode()

        if isinstance(self.commands, str):
            for prefix in self.prefixes:
                pattern = re.compile(rf'^{re.escape(prefix)}({re.escape(self.commands)})(?:\s+(.+))?$',
                                     re.DOTALL | re.IGNORECASE)
                result = check_command_args(pattern, msg_text)
                if result is not False:
                    full_command = msg_text[len(prefix):]  # Удаляем префикс
                    args = result[1] if result[1] else ''  # Получаем аргументы
                    return {'args': [full_command, self.commands, args]}
            return

        if isinstance(self.commands, list):
            for command in self.commands:
                for prefix in self.prefixes:
                    pattern = re.compile(rf'^{re.escape(prefix)}({re.escape(command)})(?:\s+(.+))?$',
                                         re.DOTALL | re.IGNORECASE)

                    result = check_command_args(pattern, msg_text)
                    if result is not False:
                        full_command = msg_text[len(prefix):]  # Удаляем префикс
                        args = result[1] if result[1] else ''  # Получаем аргументы
                        return {'args': [full_command, command, args]}