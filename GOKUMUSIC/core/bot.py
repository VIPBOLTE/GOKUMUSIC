#YO YO HONEY SINGH
import asyncio
import threading

import uvloop
from flask import Flask
from pyrogram import Client, idle
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

import config

from ..logging import LOGGER

uvloop.install()

# Flask app initialize
app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running"


def run():
    app.run(host="0.0.0.0", port=8000, debug=False)



class GOKUBOT(Client):
    def __init__(self):
        LOGGER(__name__).info(f"Starting Bot")
        super().__init__(
            "GOKUMUSIC",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
        )

    async def start(self):
        await super().start()
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.mention = self.me.mention

        # Create the button
        button = InlineKeyboardMarkup(
            [
                        [
            InlineKeyboardButton(
                text="๏ ꜱᴛᴀʀᴛ ᴛᴏ ᴘᴍ ๏",
                url=f"https://t.me/{self.username}?start=start",
            ),
           ],
             [
                    InlineKeyboardButton(
                        text="๏ ᴏᴡɴᴇʀ ๏",
                        url=f"https://t.me/LoVING_SOCIETY",
                    ),
                    InlineKeyboardButton(
                        text="๏ ᴜᴘᴅᴀᴛᴇ ๏",
                        url=f"https://t.me/channelz_k",
                    )
              ],
                [
                    InlineKeyboardButton(
                        text="๏ ᴀᴅᴅ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ๏",
                        url=f"https://t.me/{self.username}?startgroup=true",
                    )
                ]
 
            ]
        )

        # Try to send a message to the logger group
        if config.LOG_GROUP_ID:
            try:
                await self.send_photo(
                    config.LOG_GROUP_ID,
                    photo=config.BOT_IMG_URL,
                    caption=f"╔════❰💓ᴡᴇʟᴄᴏᴍᴇ💓❱════❍⊱❁۪۪\n║\n║┣⪼💫 ʙᴏᴛ sᴛᴀʀᴛᴇᴅ ʙᴀʙʏ ❤️\n║\n║┣⪼ {self.name}\n║\n║┣⪼🕊️ ɪᴅ:- `{self.id}` \n║\n║┣⪼🤡 @{self.username} \n║ \n║┣⪼💀 ᴛʜᴀɴᴋs ғᴏʀ ᴜsɪɴɢ 🌸\n║\n╚════════════════❍⊱❁",
                    reply_markup=button,
                )
            except pyrogram.errors.ChatWriteForbidden as e:
                LOGGER(__name__).error(f"Bot cannot write to the log group: {e}")
                try:
                    await self.send_message(
                        config.LOG_GROUP_ID,
                        f"╔═══❰💓ᴡᴇʟᴄᴏᴍᴇ💓❱═══❍⊱❁۪۪\n║\n║┣⪼ 💫 ʙᴏᴛ sᴛᴀʀᴛᴇᴅ ʙᴀʙʏ ❤️\n║\n║◈ {self.name}\n║\n║┣⪼🕊️ɪᴅ :- `{self.id}` \n║\n║┣⪼🤡 @{self.username} \n║ \n║┣⪼💀 ᴛʜᴀɴᴋs ғᴏʀ ᴜsɪɴɢ 🌸\n║\n╚══════════════❍⊱❁",
                        reply_markup=button,
                    )
                except Exception as e:
                    LOGGER(__name__).error(f"Failed to send message in log group: {e}")
            except Exception as e:
                LOGGER(__name__).error(
                    f"Unexpected error while sending to log group: {e}"
                )
        else:
            LOGGER(__name__).warning(
                "LOG_GROUP_ID is not set, skipping log group notifications."
            )

        # Setting commands
        if config.SET_CMDS:
            try:
                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "Start the bot"),
                        BotCommand("help", "Get the help menu"),
                        BotCommand("ping", "Check if the bot is alive or dead"),
                    ],
                    scope=BotCommandScopeAllPrivateChats(),
                )
                await self.set_bot_commands(
                    commands=[
                        BotCommand("play", "Start playing requested song"),
                        BotCommand("stop", "Stop the current song"),
                        BotCommand("pause", "Pause the current song"),
                        BotCommand("resume", "Resume the paused song"),
                        BotCommand("queue", "Check the queue of songs"),
                        BotCommand("skip", "Skip the current song"),
                        BotCommand("volume", "Adjust the music volume"),
                        BotCommand("lyrics", "Get lyrics of the song"),
                    ],
                    scope=BotCommandScopeAllGroupChats(),
                )
                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "❥ Start the bot"),
                        BotCommand("ping", "❥ Check the ping"),
                        BotCommand("help", "❥ Get help"),
                        BotCommand("vctag", "❥ Tag all for voice chat"),
                        BotCommand("stopvctag", "❥ Stop tagging for VC"),
                        BotCommand("tagall", "❥ Tag all members by text"),
                        BotCommand("cancel", "❥ Cancel the tagging"),
                        BotCommand("settings", "❥ Get the settings"),
                        BotCommand("reload", "❥ Reload the bot"),
                        BotCommand("play", "❥ Play the requested song"),
                        BotCommand("vplay", "❥ Play video along with music"),
                        BotCommand("end", "❥ Empty the queue"),
                        BotCommand("playlist", "❥ Get the playlist"),
                        BotCommand("stop", "❥ Stop the song"),
                        BotCommand("lyrics", "❥ Get the song lyrics"),
                        BotCommand("song", "❥ Download the requested song"),
                        BotCommand("video", "❥ Download the requested video song"),
                        BotCommand("gali", "❥ Reply with fun"),
                        BotCommand("shayri", "❥ Get a shayari"),
                        BotCommand("love", "❥ Get a love shayari"),
                        BotCommand("sudolist", "❥ Check the sudo list"),
                        BotCommand("owner", "❥ Check the owner"),
                        BotCommand("update", "❥ Update bot"),
                        BotCommand("gstats", "❥ Get stats of the bot"),
                        BotCommand("repo", "❥ Check the repo"),
                    ],
                    scope=BotCommandScopeAllChatAdministrators(),
                )
            except Exception as e:
                LOGGER(__name__).error(f"Failed to set bot commands: {e}")

        # Check if bot is an admin in the logger group
        if config.LOG_GROUP_ID:
            try:
                chat_member_info = await self.get_chat_member(
                    config.LOG_GROUP_ID, self.id
                )
                if chat_member_info.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).error(
                        "Please promote Bot as Admin in Logger Group"
                    )
            except Exception as e:
                LOGGER(__name__).error(f"Error occurred while checking bot status: {e}")

        LOGGER(__name__).info(f"MusicBot Started as {self.name}")
