from aiogram.types import Message

from bot.adm.admin import handle_admin_db
from bot.database import add_user
from bot.design.keyboards import Keyboards


class Commands:
    """
    Bot commands and text content handler.
    
    Features:
    - Start command handler
    - Help message formatting
    - Admin statistics access
    - User registration
    
    Text content:
    - Help guide
    - Welcome message
    - Error messages
    """

    # Command message templates
    HELP_TEXT = """
📝 <b>Requirements for Video:</b>

1️⃣ Format: <b>Square</b> <i>(recommended)</i>
2️⃣ Quality: <b>480p</b> <i>(recommended, faster processing)</i>
3️⃣ Duration: <b>Up to 60 seconds</b>
4️⃣ Size: <b>Max 20 MB</b>

📱 <b>How to Share Video Message:</b>

1. Select video message
2. Tap 'Forward'
3. Choose recipient
4. Tap 'Forward message'
5. Enable 'Hide sender's name'
6. Send

💡 <b>Tips:</b>
• Adjust video parameters before sending
• Square videos work best
• Shorter videos process faster
"""

    START_TEXT = """
👋 <b>Welcome, {name}!</b>

🎥 Convert videos to round messages
Just send any video!

<b>Commands:</b>
/start - Restart bot
/help - Usage guide
"""

    @staticmethod
    async def start(message: Message) -> None:
        """
        Handle /start command.
        
        Actions:
        1. Delete command message
        2. Register new user
        3. Send welcome message with menu
        
        Args:
            message (Message): Start command message
        """
        await message.delete()
        user = message.from_user

        add_user(
            user_id=user.id,
            username=f"@{user.username}" if user.username else "None",
            first_name=user.first_name
        )

        await message.answer(
            Commands.START_TEXT.format(name=user.first_name).strip(),
            reply_markup=Keyboards.start
        )

    @staticmethod
    async def help(message: Message) -> None:
        await message.delete()
        await message.answer(Commands.HELP_TEXT.strip())

    @staticmethod
    async def db(message: Message) -> None:
        """Handle database statistics command (admin only)"""
        await handle_admin_db(message)


start = Commands.start
help = Commands.help
db = Commands.db
