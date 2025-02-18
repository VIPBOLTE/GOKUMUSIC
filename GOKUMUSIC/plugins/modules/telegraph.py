# <======================================= IMPORTS ==================================================>
from telegraph import upload_file
from pyrogram import filters
from GOKUMUSIC import app
from pyrogram.types import Message

# <======================================= Helper Function ==========================================>
def upload_to_platform(message: Message, base_url: str):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return message.reply("⚠️ Please reply to a media file (photo/video/document).")
    
    status = message.reply("🔄 Uploading your file...")
    try:
        path = reply.download()  # Downloads the file
        file_link = upload_file(path)  # Upload the file to Telegraph or Graph

        if isinstance(file_link, list):  # In case the upload returns a list of links
            url = f"{base_url}{file_link[0]}"  # Taking the first link from the list
        else:  # In case the upload returns a single string link
            url = f"{base_url}{file_link}"

        status.edit(f"✅ Link generated successfully: `{url}`")
    except Exception as e:
        status.edit(f"❌ Failed to generate link. Error: {e}")
# <======================================= Commands ================================================>
@app.on_message(filters.command(["tele", "tgm", "telegraph"]))
def upload_to_telegraph(_, message):
    upload_to_platform(message, "https://telegra.ph")

@app.on_message(filters.command(["graph", "grf"]))
def upload_to_graph(_, message):
    upload_to_platform(message, "https://graph.org")
