import logging
import sys
from datetime import datetime
from pathlib import Path

import moviepy.config as mp_config
from aiogram.exceptions import TelegramEntityTooLarge
from aiogram.types import Message, FSInputFile
from moviepy.editor import VideoFileClip

from bot.database import error, usage
from data.cfg import STICKER

# Completely suppress MoviePy output
mp_config.LOGGER = logging.getLogger('moviepy')
mp_config.LOGGER.setLevel(logging.ERROR)


class NullWriter:
    """
    Utility class to suppress stdout output.
    Used to prevent MoviePy from printing progress bars and processing information.
    """

    def write(self, text): pass

    def flush(self): pass


def cleanup_temp_files(user_id: int, *paths: Path) -> None:
    """
    Clean up temporary files created during video processing.
    
    Args:
        user_id (int): User ID to identify user-specific files
        *paths (Path): Specific file paths to remove
        
    Note:
        Removes both specified files and any remaining files matching the user_id pattern
        in the cache directory to prevent storage buildup.
    """
    temp_dir = Path("cache")
    if temp_dir.exists():
        # Remove specific files first
        for path in paths:
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                pass

        # Remove any remaining user files
        for file in temp_dir.glob(f"*[{user_id}]*"):
            try:
                file.unlink()
            except OSError:
                pass


async def video(message: Message):
    """
    Process video messages into circular video notes.
    
    Args:
        message (Message): Incoming message containing video
        
    Processing workflow:
    1. Validate video parameters (size, duration)
    2. Download and save to temporary storage
    3. Process video:
        - Resize maintaining aspect ratio
        - Crop to circular shape
        - Convert to video note format
    4. Send processed video note
    5. Clean up temporary files
    
    Error handling:
    - File size limits (20MB max)
    - Processing errors
    - Network errors
    
    Notes:
        - Uses cache directory for temporary files
        - Suppresses MoviePy output during processing
        - Auto-deletes original message
    """
    user_id = message.from_user.id
    username = message.from_user.username or "None"
    current_time = datetime.now().strftime("%H-%M-%S-%f")

    # Initialize paths
    temp_dir = Path("cache")
    temp_dir.mkdir(exist_ok=True)

    input_path = temp_dir / f"[{user_id}]_({current_time})_video.mp4"
    output_path = temp_dir / f"[{user_id}]_({current_time})_output_video.mp4"

    try:
        # Delete user's message first
        await message.delete()

        file_id = message.video.file_id
        file = await message.bot.get_file(file_id)

        processing_message = await message.answer_sticker(sticker=STICKER)

        # Set MoviePy's temp directory to our cache
        mp_config.TEMP_DIR = str(temp_dir)

        await message.bot.download_file(file.file_path, input_path)

        # Suppress MoviePy output during processing
        old_stdout = sys.stdout
        sys.stdout = NullWriter()

        try:
            with VideoFileClip(str(input_path)) as input_video:
                w, h = input_video.size
                circle_size = 360
                aspect_ratio = float(w) / float(h)

                if w > h:
                    new_w = int(circle_size * aspect_ratio)
                    new_h = circle_size
                else:
                    new_w = circle_size
                    new_h = int(circle_size / aspect_ratio)

                resized_video = input_video.resize((new_w, new_h))
                output_video = resized_video.crop(
                    x_center=resized_video.w / 2,
                    y_center=resized_video.h / 2,
                    width=circle_size,
                    height=circle_size
                )
                output_video.write_videofile(
                    str(output_path),
                    codec="libx264",
                    audio_codec="aac",
                    bitrate="5M",
                    verbose=False,
                    logger=None
                )
        finally:
            # Restore stdout
            sys.stdout = old_stdout

        video_note = FSInputFile(output_path, filename=f"{user_id}_{current_time}_output_video.mp4")
        await message.bot.send_video_note(chat_id=message.chat.id, video_note=video_note,
                                          duration=int(output_video.duration),
                                          length=circle_size)

        usage(user_id)

        await processing_message.delete()

    except TelegramEntityTooLarge:
        await message.reply("⚠️ The file is too large.\nPlease send a file smaller than 20 MB.")
    except Exception as e:
        await message.reply("❌ An error occurred during processing. Please contact the developer.")
        error(user_id, username, str(e))

    finally:
        # Clean up all temporary files
        cleanup_temp_files(user_id, input_path, output_path)


async def handle_unknown_input(message: Message):
    """
    Handle unrecognized message types with a helpful response.
    
    Args:
        message (Message): Unrecognized message
    
    Note:
        Helps maintain clean chat history while guiding users
        to proper bot usage.
    """
    await message.delete()

    await message.answer(
        "📹 Please send a video or use these commands:\n"
        "/start - Launch the bot\n"
        "/help - View usage guide"
    )
