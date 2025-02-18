import base64
import httpx
import os
import requests 
from pyrogram import filters
from config import BOT_USERNAME
from GOKUMUSIC import app
from pyrogram import filters
import pyrogram
from uuid import uuid4
from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup

import cv2
import numpy as np

@app.on_message(filters.reply & filters.command("upscale"))
async def upscale_image(app, message):
    try:
        if not message.reply_to_message or not message.reply_to_message.photo:
            await message.reply_text("Please reply to an image to upscale it.")
            return

        image = message.reply_to_message.photo.file_id
        file_path = await app.download_media(image)

        # Read the image
        img = cv2.imread(file_path)

        # Upscale the image
        upscaled_img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Save the upscaled image
        upscaled_file_path = "upscaled.png"
        cv2.imwrite(upscaled_file_path, upscaled_img)

        # Send the upscaled image
        await app.send_photo(
            message.chat.id,
            photo=upscaled_file_path,
            caption="Here is the upscaled image!",
        )

        # Clean up files
        os.remove(file_path)
        os.remove(upscaled_file_path)

    except Exception as e:
        print(f"Failed to upscale the image: {e}")
        await message.reply_text("Failed to upscale the image. Please try again later.")
