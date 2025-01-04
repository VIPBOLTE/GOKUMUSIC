import asyncio
import os
import time
from time import time

import wget
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL

from GOKUMUSIC import app
from GOKUMUSIC.platforms.download import cookies as cookie_txt_file

# Define a dictionary to track the last query timestamp for each user
user_last_CallbackQuery_time = {}
user_CallbackQuery_count = {}

# Define the threshold for query spamming (e.g., 1 query within 60 seconds)
SPAM_THRESHOLD = 1
SPAM_WINDOW_SECONDS = 30

SPAM_AUDIO_THRESHOLD = 1
SPAM_AUDIO_WINDOW_SECONDS = 30

BANNED_USERS = []


@app.on_callback_query(filters.regex("downloadvideo") & ~filters.user(BANNED_USERS))
async def download_video(client, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    current_time = time.time()

    # Check if the user has exceeded the query limit
    last_Query_time = user_last_CallbackQuery_time.get(user_id, 0)
    if current_time - last_Query_time < SPAM_WINDOW_SECONDS:
        # If the limit is exceeded, send a response and return
        await CallbackQuery.answer(
            "➻ ʏᴏᴜ ʜᴀᴠᴇ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ʏᴏᴜʀ ᴠɪᴅᴇᴏ (ᴄʜᴇᴄᴋ ᴍʏ ᴅᴍ/ᴘᴍ).\n\n➥ ɴᴇxᴛ sᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅ ᴀғᴛᴇʀ 30 sᴇᴄᴏɴᴅs.",
            show_alert=True,
        )
        return
    else:
        # Update the last query time and query count
        user_last_CallbackQuery_time[user_id] = current_time
        user_CallbackQuery_count[user_id] = user_CallbackQuery_count.get(user_id, 0) + 1

    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    user_name = CallbackQuery.from_user.first_name
    chutiya = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    await CallbackQuery.answer("ᴏᴋ sɪʀ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...", show_alert=True)
    pablo = await client.send_message(
        CallbackQuery.message.chat.id,
        f"**ʜᴇʏ {chutiya} ᴅᴏᴡɴʟᴏᴅɪɴɢ ʏᴏᴜʀ ᴠɪᴅᴇᴏ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...**",
    )
    if not videoid:
        await pablo.edit(
            f"**ʜᴇʏ {chutiya} ʏᴏᴜʀ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ. ᴛʀʏ ᴀɢᴀɪɴ...**"
        )
        return

    search = SearchVideos(
        f"https://youtube.com/{videoid}", offset=1, mode="dict", max_results=1
    )
    mi = search.result()
    mio = mi.get("search_result", [])
    if not mio:
        await pablo.edit(
            f"**ʜᴇʏ {chutiya} ʏᴏᴜʀ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ. ᴛʀʏ ᴀɢᴀɪɴ...**"
        )
        return

    mo = mio[0].get("link", "")
    thum = mio[0].get("title", "")
    fridayz = mio[0].get("id", "")
    thums = mio[0].get("channel", "")
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
        "cookiefile": cookie_txt_file(),
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)

    except Exception as e:
        await pablo.edit(
            f"**ʜᴇʏ {chutiya} ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ sᴏɴɢ.** \n**ᴇʀʀᴏʀ:** `{str(e)}`"
        )
        return

    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"❄ **ᴛɪᴛʟᴇ :** [{thum}]({mo})\n\n💫 **ᴄʜᴀɴɴᴇʟ :** {thums}\n\n🥀 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {chutiya}"
    try:
        await client.send_video(
            CallbackQuery.from_user.id,
            video=open(file_stark, "rb"),
            duration=int(ytdl_data["duration"]),
            file_name=str(ytdl_data["title"]),
            thumb=sedlyf,
            caption=capy,
            supports_streaming=True,
            progress_args=(
                pablo,
                f"**{chutiya} ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...**\n\n**ᴜᴘʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ...💫**",
                file_stark,
            ),
        )
        await client.send_message(
            CallbackQuery.message.chat.id,
            f"**ʜᴇʏ** {chutiya}\n\n**✅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ.**\n**➻ ᴠɪᴅᴇᴏ sᴇɴᴛ ɪɴ ʏᴏᴜʀ ᴘᴍ/ᴅᴍ.**\n**➥ ᴄʜᴇᴄᴋ ʜᴇʀᴇ » [ʙᴏᴛ ᴘᴍ/ᴅᴍ](tg://openmessage?user_id={app.id})**🤗",
        )
        await pablo.delete()
        for files in (sedlyf, file_stark):
            if files and os.path.exists(files):
                os.remove(files)

    except Exception as e:
        await pablo.delete()
        return await client.send_message(
            CallbackQuery.message.chat.id,
            f"**ʜᴇʏ {chutiya} ᴘʟᴇᴀsᴇ ᴜɴʙʟᴏᴄᴋ ᴍᴇ ғᴏʀ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ᴠɪᴅᴇᴏ ʙʏ ᴄʟɪᴄᴋ ʜᴇʀᴇ 👇👇**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"👉ᴜɴʙʟᴏᴄᴋ ᴍᴇ🤨",
                            url=f"https://t.me/{app.username}?start=info_{videoid}",
                        )
                    ]
                ]
            ),
        )


import os
import time

# Dicts to keep track of user query count and last query time
user_last_CallbackQuery_time = {}
user_CallbackQuery_count = {}


@app.on_callback_query(filters.regex("downloadaudio") & ~filters.user(BANNED_USERS))
async def download_audio(client, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    current_time = time.time()

    # Check if the user has exceeded the query limit
    last_Query_time = user_last_CallbackQuery_time.get(user_id, 0)
    if current_time - last_Query_time < SPAM_AUDIO_WINDOW_SECONDS:
        # If the limit is exceeded, send a response and return
        await CallbackQuery.answer(
            "➻ ʏᴏᴜ ʜᴀᴠᴇ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ʏᴏᴜʀ ᴀᴜᴅɪᴏ (ᴄʜᴇᴄᴋ ᴍʏ ᴅᴍ/ᴘᴍ).\n\n➥ ɴᴇxᴛ sᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅ ᴀғᴛᴇʀ 30 sᴇᴄᴏɴᴅs.",
            show_alert=True,
        )
        return
    else:
        # Update the last query time and query count
        user_last_CallbackQuery_time[user_id] = current_time
        user_CallbackQuery_count[user_id] = user_CallbackQuery_count.get(user_id, 0) + 1

    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    user_name = CallbackQuery.from_user.first_name
    chutiya = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    await CallbackQuery.answer("ᴏᴋ sɪʀ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...", show_alert=True)
    pablo = await client.send_message(
        CallbackQuery.message.chat.id,
        f"**ʜᴇʏ {chutiya} ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ʏᴏᴜʀ ᴀᴜᴅɪᴏ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...**",
    )
    if not videoid:
        await pablo.edit(
            f"**ʜᴇʏ {chutiya} ʏᴏᴜʀ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ. ᴛʀʏ ᴀɢᴀɪɴ...**"
        )
        return

    search = SearchVideos(
        f"https://youtube.com/{videoid}", offset=1, mode="dict", max_results=1
    )
    mi = search.result()
    mio = mi.get("search_result", [])
    if not mio:
        await pablo.edit(
            f"**ʜᴇʏ {chutiya} ʏᴏᴜʀ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ. ᴛʀʏ ᴀɢᴀɪɴ...**"
        )
        return

    mo = mio[0].get("link", "")
    thum = mio[0].get("title", "")
    fridayz = mio[0].get("id", "")
    thums = mio[0].get("channel", "")
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "bestaudio/best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "outtmpl": "%(id)s.mp3",  # Output format changed to mp3
        "logtostderr": False,
        "quiet": True,
        "cookiefile": cookie_txt_file(),
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)

    except Exception as e:
        await pablo.edit(
            f"**ʜᴇʏ {chutiya} ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ᴀᴜᴅɪᴏ.** \n**ᴇʀʀᴏʀ:** `{str(e)}`"
        )
        return

    file_stark = f"{ytdl_data['id']}.mp3"  # Adjusted file extension
    capy = f"❄ **ᴛɪᴛʟᴇ :** [{thum}]({mo})\n\n💫 **ᴄʜᴀɴɴᴇʟ :** {thums}\n\n🥀 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {chutiya}\n\n⏳ **ᴅᴜʀᴀᴛɪᴏɴ :** {int(ytdl_data['duration']) // 60}:{int(ytdl_data['duration']) % 60}"
    try:
        await client.send_audio(
            CallbackQuery.from_user.id,
            audio=open(file_stark, "rb"),
            title=str(ytdl_data["title"]),
            thumb=sedlyf,
            caption=capy,
            progress_args=(
                pablo,
                f"**{chutiya} ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...**\n\n**ᴜᴘʟᴏᴀᴅɪɴɢ ᴀᴜᴅɪᴏ ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ...💫**",
                file_stark,
            ),
        )
        await client.send_message(
            CallbackQuery.message.chat.id,
            f"ʜᴇʏ {chutiya}**\n\n✅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ.**\n**➻ ᴀᴜᴅɪᴏ sᴇɴᴛ ɪɴ ʏᴏᴜʀ ᴘᴍ/ᴅᴍ.**\n**➥ ᴄʜᴇᴄᴋ ʜᴇʀᴇ » [ʙᴏᴛ ᴘᴍ/ᴅᴍ](tg://openmessage?user_id={app.id})**🤗",
        )

        await pablo.delete()
        for files in (sedlyf, file_stark):
            if files and os.path.exists(files):
                os.remove(files)

    except Exception as e:
        await pablo.delete()
        return await client.send_message(
            CallbackQuery.message.chat.id,
            f"**ʜᴇʏ {chutiya} ᴘʟᴇᴀsᴇ ᴜɴʙʟᴏᴄᴋ ᴍᴇ ғᴏʀ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ᴀᴜᴅɪᴏ ʙʏ ᴄʟɪᴄᴋ ʜᴇʀᴇ 👇👇**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"👉ᴜɴʙʟᴏᴄᴋ ᴍᴇ🤨",
                            url=f"https://t.me/{app.username}?start=info_{videoid}",
                        )
                    ]
                ]
            ),
    )
