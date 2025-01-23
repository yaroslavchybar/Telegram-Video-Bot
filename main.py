import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.database import initialize_db
from bot.router import setup_routers
from data.cfg import TOKEN


class BotApplication:
    def __init__(self):
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        dispatcher_logger = logging.getLogger('aiogram.dispatcher')
        dispatcher_logger.setLevel(logging.INFO)

        self.bot: Bot | None = None
        self.dp: Dispatcher | None = None

    async def start(self) -> None:
        """Start the bot application."""
        try:
            initialize_db()

            default = DefaultBotProperties(parse_mode=ParseMode.HTML)
            self.bot = Bot(token=TOKEN, default=default)
            self.dp = Dispatcher(storage=MemoryStorage())

            setup_routers(self.dp)
            await self.dp.start_polling(self.bot)

        except Exception as e:
            logging.error(f"Critical error: {e}")
            raise

    async def stop(self) -> None:
        if self.bot:
            await self.bot.session.close()


async def main() -> None:
    app = BotApplication()
    try:
        await app.start()
    except (KeyboardInterrupt, SystemExit):
        await app.stop()
    except Exception as e:
        logging.error(f"Fatal error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
