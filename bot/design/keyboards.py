from typing import ClassVar

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.cfg import DEV


class Keyboards:
    """Class containing all keyboard markups"""

    start: ClassVar[InlineKeyboardMarkup] = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👨‍💻 Developer", url=DEV)],
            [InlineKeyboardButton(text="📖 How to Use", callback_data="help")]
        ]
    )

    back: ClassVar[InlineKeyboardMarkup] = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Back", callback_data="back")]
        ]
    )

    admin_stats: ClassVar[InlineKeyboardMarkup] = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Show All Errors", callback_data="show_errors")]
        ]
    )

    admin_back: ClassVar[InlineKeyboardMarkup] = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Back to Stats", callback_data="back_to_stats")]
        ]
    )
