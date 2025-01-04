import asyncio

from BADMUSIC import app
from pyrogram import filters
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

@Client.on_message(filters.command(["repo"], prefixes=["."]))
async def start(client: Client, message: Message):
    await message.reply_video(
        video=f"https://telegra.ph/file/bda2c51bd00c8f4710b04.mp4",
        caption=f"❤️ ʜᴇʏ {message.from_user.mention} [☆ ʀᴇᴘᴏ 💗](https://github.com/Badhacker98/BADMUSIC/fork)",
        reply_markup=InlineKeyboardMarkup(
            [
               [
            InlineKeyboardButton(
                text="☆ ᴏᴡɴᴇʀ 💗 ", url=f"https://t.me/Zindagi_hai_tere_nal"
            ),
            InlineKeyboardButton(
                text="☆ ɢʀᴏᴜᴘ 💗", url=f"https://t.me/LOVING_SOCIETY"
            ),
        ],
          [
            InlineKeyboardButton(
                text="☆ ᴄʜᴀɴɴᴇʟ 💗 ", url=f"https://t.me/channelz_k"
            ),
            InlineKeyboardButton(
                text="☆ ʀᴇᴘᴏ 💗", url=f"https://github.com/Badhacker98/BADMUSIC/fork"
            ),
        ],
                [
                    InlineKeyboardButton(
                        "✯ ᴄʟᴏsᴇ ✯", callback_data="close"
                    )
                ],
            ]
        )
    )
  
