from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def bot_add_to_chat_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Добавить бота',
                url='https://t.me/UpGreenDayGroup?startgroup=Green&admin=change_info+'
                    'restrict_members+delete_messages+pin_messages+invite_users')
            ]
        ]
    )
    return keyboard


def add_bot_administration_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='⭐️ Назначить администратором',
                url='https://t.me/SupHlpBot?startgroup=Sup&admin=change_info+restrict_members+delete_messages+'
                    'pin_messages+invite_users+promote_members+manage_voice_chats+ban_members+view_members')
            ]
        ]
    )
    return keyboard