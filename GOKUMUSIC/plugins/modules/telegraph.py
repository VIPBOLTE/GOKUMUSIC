import requests
import os
from pyrogram import filters
from GOKUMUSIC import app

# Function to upload video to Catbox (MP4, WebM, MOV supported)
def upload_to_catbox(file_path):
    url = "https://catbox.moe/user/api.php"
    with open(file_path, "rb") as file:
        response = requests.post(
            url,
            data={"reqtype": "fileupload"},
            files={"fileToUpload": file}
        )
        if response.status_code == 200 and response.text.startswith("https"):
            return response.text
        else:
            return "Failed to upload to Catbox."

# Function to upload video to GoFile.io
def upload_to_gofile(file_path):
    response = requests.post(
        "https://store1.gofile.io/uploadFile",
        files={"file": open(file_path, "rb")}
    )
    if response.status_code == 200:
        return response.json()["data"]["downloadPage"]
    return "Failed to upload to GoFile."

# Function to upload to 0x0
def upload_to_0x0(file_path):
    url = "https://0x0.st"
    with open(file_path, "rb") as file:
        response = requests.post(url, files={"file": file})
        if response.status_code == 200:
            return response.text.strip()
        return "Failed to upload to 0x0."

# Pyrogram handler for /tgm command
@app.on_message(filters.command("tgm") & filters.reply)
async def send_video_links(client, message):
    reply = message.reply_to_message
    if reply and (reply.video or reply.document or reply.photo):
        try:
            processing_message = await message.reply("Processing... Please wait.")

            # Download the media
            path = await reply.download()
            
            # Check file type
            if path.lower().endswith(('.mp4', '.mov', '.webm', '.avi', '.mkv', '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.docx')):
                catbox_url = gofile_url = x0_url = None

                # Upload to Catbox
                try:
                    catbox_url = upload_to_catbox(path)
                except Exception:
                    catbox_url = "Failed to upload to Catbox."

                # Upload to GoFile
                try:
                    gofile_url = upload_to_gofile(path)
                except Exception:
                    gofile_url = "Failed to upload to GoFile."

                # Upload to 0x0
                try:
                    x0_url = upload_to_0x0(path)
                except Exception:
                    x0_url = "Failed to upload to 0x0."

                # Send links
                await message.reply(
                    text=f"🎥 **Video Uploaded Successfully!** 🎥\n\n"
                         f"🔹 **Catbox Link:** {catbox_url}\n"
                         f"🔹 **GoFile Link:** {gofile_url}\n"
                         f"🔹 **0x0 Link:** {x0_url}"
                )
                await processing_message.delete()
            else:
                await message.reply("⚠️ Please reply to a valid **image, video, or document**.")
        except Exception as e:
            await message.reply(f"⚠️ Upload Failed: {str(e)}")
        finally:
            if os.path.exists(path):
                os.remove(path)
    else:
        await message.reply("⚠️ Please reply to a **photo, video, or document**.")

