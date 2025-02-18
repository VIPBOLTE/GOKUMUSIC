from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode
import config
from ..logging import LOGGER
import yt_dlp  # Import yt-dlp to handle YouTube downloads
import os

class GOKU(Client):
    def __init__(self):
        LOGGER(__name__).info(f"Starting Bot...")
        super().__init__(
            name="UTOPIA",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b><u>\n\nɪᴅ : <code>{self.id}</code>\nɴᴀᴍᴇ : {self.name}\nᴜsᴇʀɴᴀᴍᴇ : @{self.username}",
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "Bot has failed to access the log group/channel. Make sure that you have added your bot to your log group/channel."
            )
            exit()
        except Exception as ex:
            LOGGER(__name__).error(
                f"Bot has failed to access the log group/channel.\n  Reason : {type(ex).__name__}."
            )
            exit()

        a = await self.get_chat_member(config.LOGGER_ID, self.id)
        if a.status != ChatMemberStatus.ADMINISTRATOR:
            LOGGER(__name__).error(
                "Please promote your bot as an admin in your log group/channel."
            )
            exit()
        LOGGER(__name__).info(f"Music Bot Started as {self.name}")

        # Initialize yt-dlp with cookies.txt
        self.yt_dlp_opts = {
            'format': 'bestaudio/best',   # Default to the best audio format
            'noplaylist': True,           # Don't download playlists
            'cookiefile': 'cookies.txt',  # Path to your cookies.txt file
        }

    async def stop(self):
        await super().stop()

    # New method to handle YouTube download requests
    async def download_youtube_video(self, url: str):
        try:
            with yt_dlp.YoutubeDL(self.yt_dlp_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Unknown')
                video_url = info.get('url', None)
                
                if video_url:
                    return f"Successfully fetched: {video_title}\nURL: {video_url}"
                else:
                    return "Failed to fetch video URL."
        except Exception as e:
            LOGGER(__name__).error(f"Error downloading YouTube video: {str(e)}")
            return f"An error occurred: {str(e)}"
