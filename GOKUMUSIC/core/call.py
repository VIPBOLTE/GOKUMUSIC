import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded

import config
from GOKUMUSIC import LOGGER, YouTube, app
from GOKUMUSIC.music import db
from GOKUMUSIC.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from GOKUMUSIC.utils.exceptions import AssistantErr
from GOKUMUSIC.utils.formatters import check_duration, seconds_to_min, speed_converter
from GOKUMUSIC.utils.inline.play import stream_markup
from GOKUMUSIC.utils.stream.autoclear import auto_clean
from GOKUMUSIC.utils.thumbnails import get_thumb
from Strings import get_string

autoend = {}
counter = {}


async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="GOKUAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(
            self.userbot1,
            cache_duration=100,
        )
        self.userbot2 = Client(
            name="GOKUAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(
            self.userbot2,
            cache_duration=100,
        )
        self.userbot3 = Client(
            name="GOKUAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(
            self.userbot3,
            cache_duration=100,
        )
        self.userbot4 = Client(
            name="GOKUAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(
            self.userbot4,
            cache_duration=100,
        )
        self.userbot5 = Client(
            name="GOKUAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(
            self.userbot5,
            cache_duration=100,
        )

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error during stop_stream: {e}")

    async def stop_stream_force(self, chat_id: int):
        try:
            if config.STRING1:
                await self.one.leave_group_call(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error leaving group call with STRING1: {e}")
        try:
            if config.STRING2:
                await self.two.leave_group_call(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error leaving group call with STRING2: {e}")
        try:
            if config.STRING3:
                await self.three.leave_group_call(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error leaving group call with STRING3: {e}")
        try:
            if config.STRING4:
                await self.four.leave_group_call(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error leaving group call with STRING4: {e}")
        try:
            if config.STRING5:
                await self.five.leave_group_call(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error leaving group call with STRING5: {e}")
        try:
            await _clear_(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error during _clear_: {e}")

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != str("1.0"):
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                if str(speed) == str("0.5"):
                    vs = 2.0
                if str(speed) == str("0.75"):
                    vs = 1.35
                if str(speed) == str("1.5"):
                    vs = 0.68
                if str(speed) == str("2.0"):
                    vs = 0.5
                proc = await asyncio.create_subprocess_shell(
                    cmd=(f"ffmpeg -i {file_path} -filter:v setpts={vs}*PTS -filter:a atempo={speed} {out}"),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
            else:
                pass
        else:
            out = file_path
        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        stream = (
            AudioVideoPiped(
                out,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
                additional_ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
            if playing[0]["streamtype"] == "video"
            else AudioPiped(
                out,
                audio_parameters=HighQualityAudio(),
                additional_ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
        )
        if str(db[chat_id][0]["file"]) == str(file_path):
            await assistant.change_stream(chat_id, stream)
        else:
            raise AssistantErr("Umm")
        if str(db[chat_id][0]["file"]) == str(file_path):
            exis = (playing[0]).get("old_dur")
            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except Exception as e:
            LOGGER(__name__).error(f"Error during force_stop_stream: {e}")
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error during force_stop_stream (leave call): {e}")

    async def skip_stream(self, chat_id: int, link: str, video: Union[bool, str] = None, image: Union[bool, str] = None):
        assistant = await group_assistant(self, chat_id)
        if video:
            stream = AudioVideoPiped(
                link,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
            )
        else:
            stream = AudioPiped(link, audio_parameters=HighQualityAudio())
        await assistant.change_stream(chat_id, stream)

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        stream = (
            AudioVideoPiped(
                file_path,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
            if mode == "video"
            else AudioPiped(
                file_path,
                audio_parameters=HighQualityAudio(),
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        )
        await assistant.change_stream(chat_id, stream)

    async def loop_stream(self, chat_id: int, file_path: str):
        try:
            loop = await get_loop(chat_id)
            if loop == "on":
                await set_loop(chat_id, "off")
                await self.skip_stream(chat_id, file_path)
            else:
                await set_loop(chat_id, "on")
                await self.skip_stream(chat_id, file_path)
        except Exception as e:
            LOGGER(__name__).error(f"Error during loop_stream: {e}")
