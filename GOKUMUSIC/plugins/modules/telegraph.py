# <======================================= IMPORTS ==================================================>
from telegraph import upload_file
from pyrogram import filters
from GOKUMUSIC import app
from pyrogram.types import Message
import os

# <======================================= Helper Function ==========================================>
def upload_to_platform(message: Message, base_url: str):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return message.reply("⚠️ Please reply to a media file (photo/video/document).")

    status = message.reply("🔄 Uploading your file...")

    try:
        path = reply.download()
        if not path:
            return status.edit("❌ Failed to download the file.")

        # Check file size limit (Telegraph supports max ~5MB)
        if os.path.getsize(path) > 5242880:  # 5MB limit
            os.remove(path)
            return status.edit("⚠️ File too large! Telegraph only supports up to 5MB.")

        file_link = upload_file(path)  # Upload the file
        os.remove(path)  # Delete local file after upload

        # 🛠️ FIX: Check if file_link is a list or a string
        if isinstance(file_link, list) and len(file_link) > 0:
            url = f"{base_url}/{file_link[0]}"
        elif isinstance(file_link, str) and file_link.startswith("/"):  # Single URL case
            url = f"{base_url}/{file_link}"
        else:
            return status.edit("❌ Unexpected error: No link returned.")

        status.edit(f"✅ Link generated successfully:\n🔗 `{url}`")
    except Exception as e:
        status.edit(f"❌ Failed to generate link.\nError: `{str(e)}`")

# <======================================= Commands ================================================>
@app.on_message(filters.command(["tele", "tgm", "telegraph"]))
def upload_to_telegraph(_, message: Message):
    upload_to_platform(message, "https://telegra.ph")

@app.on_message(filters.command(["graph", "grf"]))
def upload_to_graph(_, message: Message):
    upload_to_platform(message, "https://graph.org")
