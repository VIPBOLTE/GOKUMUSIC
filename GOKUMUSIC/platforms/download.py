import asyncio
import glob
import os
import random
import re
from typing import Union

from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from yt_dlp import YoutubeDL


def cookies():
    folder_path = f"{os.getcwd()}/cookies"
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return f"""cookies/{str(cookie_txt_file).split("/")[-1]}"""


def get_ytdl_options(ytdl_opts, commamdline=True) -> Union[str, dict, list]:
    if commamdline:
        if isinstance(ytdl_opts, list):
            if os.getenv("TOKEN_ALLOW") == True:
                ytdl_opts += ["--username", "oauth2", "--password", "''"]
            else:
                ytdl_opts += ["--cookies", cookies()]
        elif isinstance(ytdl_opts, str):
            if os.getenv("TOKEN_ALLOW") == True:
                ytdl_opts += "--username oauth2 --password '' "
            else:
                ytdl_opts += f"--cookies {cookies()}"
        elif isinstance(ytdl_opts, dict):
            if os.getenv("TOKEN_ALLOW") == True:
                ytdl_opts.update({"username": "oauth2", "password": ""})
            else:
                ytdl_opts["cookiefile"] = cookies()
    else:
        if isinstance(ytdl_opts, list):
            if os.getenv("TOKEN_ALLOW") == True:
                ytdl_opts += ["username", "oauth2", "password", "''"]
            else:
                ytdl_opts += ["cookiefile", cookies()]
        elif isinstance(ytdl_opts, str):
            if os.getenv("TOKEN_ALLOW") == True:
                ytdl_opts += "username oauth2 password '' "
            else:
                ytdl_opts += f"cookiefile {cookies()}"
        elif isinstance(ytdl_opts, dict):
            if os.getenv("TOKEN_ALLOW") == True:
                ytdl_opts.update({"username": "oauth2", "password": ""})
            else:
                ytdl_opts["cookiefile"] = cookies()

    return ytdl_opts


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")
