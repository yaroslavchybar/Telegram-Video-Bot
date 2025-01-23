from aiogram import F, Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from bot.adm.admin import handle_all_errors, handle_admin_db
from bot.design.commands import Commands
from bot.design.keyboards import Keyboards
from bot.handlers import video, handle_unknown_input


class BotRouter:
    """
    Main router class handling all bot interactions.
    
    Responsibilities:
    - Command registration
    - Callback handling
    - Message routing
    - State management
    
    Structure:
    - Commands: /start, /help, /db
    - Callbacks: help, back
    - Message handlers: video, unknown
    """

    def __init__(self):
        """Initialize router and set up all handlers."""
        self.router = Router()
        self._setup_commands()
        self._setup_callbacks()
        self._setup_handlers()

    def _setup_commands(self):
        self.router.message.register(Commands.start, Command("start"))
        self.router.message.register(Commands.help, Command("help"))
        self.router.message.register(Commands.db, Command("db"))

    def _setup_callbacks(self):
        self.router.callback_query.register(self._help_callback, F.data == "help")
        self.router.callback_query.register(self._back_callback, F.data == "back")
        self.router.callback_query.register(handle_all_errors, F.data == "show_errors")
        self.router.callback_query.register(handle_admin_db, F.data == "back_to_stats")

    def _setup_handlers(self):
        self.router.message.register(video, F.video)
        self.router.message.register(handle_unknown_input)

    @staticmethod
    async def _help_callback(callback: CallbackQuery):
        await callback.message.edit_text(
            Commands.HELP_TEXT.strip(),
            reply_markup=Keyboards.back
        )
        await callback.answer()

    @staticmethod
    async def _back_callback(callback: CallbackQuery):
        await callback.message.edit_text(
            Commands.START_TEXT.format(name=callback.from_user.first_name).strip(),
            reply_markup=Keyboards.start
        )
        await callback.answer()


def setup_routers(dp: Dispatcher):
    """Initialize and connect router to dispatcher"""
    bot_router = BotRouter()
    dp.include_router(bot_router.router)
