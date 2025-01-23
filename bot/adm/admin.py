from aiogram.types import Message, CallbackQuery

from bot.database import statistics, errors_count, get_all_errors
from bot.design.keyboards import Keyboards
from data.cfg import ADMIN_ID


async def is_admin(message: Message | CallbackQuery) -> bool:
    """Check if the user is an admin"""
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        if isinstance(message, Message):
            await message.answer("⛔️ Access denied")
        else:
            await message.answer("⛔️ Access denied", show_alert=True)
        return False
    return True


async def handle_admin_db(callback_or_message: Message | CallbackQuery) -> None:
    """Handle admin database statistics command"""
    if isinstance(callback_or_message, CallbackQuery):
        message = callback_or_message.message
        await callback_or_message.answer()
    else:
        message = callback_or_message
        await message.delete()

    if not await is_admin(callback_or_message):
        return

    users, uses = statistics()
    error_count = errors_count()
    recent_errors = get_all_errors(3)

    error_preview = "\n".join(
        f"  • {error['username']} - {error['error_message']} ({error['timestamp']})"
        for error in recent_errors
    )

    stats_message = f"""
📊 <b>Bot Statistics Dashboard</b>

<b>General Statistics:</b>
👥 Total Users: {users:,}
🔄 Total Uses: {uses:,}
❌ Total Errors: {error_count:,}
"""

    if isinstance(callback_or_message, CallbackQuery):
        await message.edit_text(stats_message, reply_markup=Keyboards.admin_stats)
    else:
        await message.answer(stats_message, reply_markup=Keyboards.admin_stats)


async def handle_all_errors(callback: CallbackQuery) -> None:
    """Handle showing all errors"""
    if not await is_admin(callback):
        return

    all_errors = get_all_errors()

    if not all_errors:
        await callback.answer("No errors found", show_alert=True)
        return

    error_text = "\n\n".join(
        f"🔴 <b>Error #{i + 1}</b>\n"
        f"<b>User:</b> @{error['username']}\n"
        f"<b>Time:</b> {error['timestamp']}\n"
        f"<b>Message:</b> {error['error_message']}"
        for i, error in enumerate(all_errors)
    )

    message = f"""
📋 <b>All Error Logs</b>
Total errors: {len(all_errors)}

<blockquote expandable>{error_text}</blockquote>
"""

    if len(message) > 4000:
        message = message[:4000] + "\n\n... (message truncated)"

    await callback.message.edit_text(message, reply_markup=Keyboards.admin_back)
