import os
import re
import random
import aiofiles
import aiohttp

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from GOKUMUSIC import app
from config import YOUTUBE_IMG_URL

# Resize Image Function
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

# Clear long text for image overlay
def clear(text):
    words = text.split(" ")
    title = ""
    for word in words:
        if len(title) + len(word) < 60:
            title += " " + word
    return title.strip()

# Fetch YouTube Thumbnail & Create Image
async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    # Search for video details
    try:
        results = VideosSearch(videoid, limit=1)  # Use videoid only, not full URL
        response = await results.next()
        
        if not response or "result" not in response:
            print(f"Error: No results found for video ID: {videoid}")
            return YOUTUBE_IMG_URL  # Return default image

        result = response["result"][0]  # Get first result safely
        title = re.sub("\W+", " ", result.get("title", "Unsupported Title")).title()
        duration = result.get("duration", None)  # Duration may be None for LIVE videos
        thumbnail = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")

        # Handle LIVE videos
        duration_text = "🔴 LIVE" if duration is None else duration

        # Download Thumbnail Image
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    file_path = f"cache/thumb{videoid}.png"
                    async with aiofiles.open(file_path, mode="wb") as f:
                        await f.write(await resp.read())

        # Open Image & Process
        try:
            youtube = Image.open(file_path)
        except Exception as e:
            print(f"Error opening image: {e}")
            return YOUTUBE_IMG_URL  # Use fallback if image fails

        # Apply Effects
        colors = ["white", "red", "orange", "yellow", "green", "cyan", "azure", "blue", "violet", "magenta", "pink"]
        border = random.choice(colors)
        image1 = changeImageSize(1280, 720, youtube)
        bg_bright = ImageEnhance.Brightness(image1).enhance(1.1)
        bg_logo = ImageEnhance.Contrast(bg_bright).enhance(1.1)
        logox = ImageOps.expand(bg_logo, border=7, fill=border)
        background = changeImageSize(1280, 720, logox)

        # Load Fonts
        font_path = "GOKUMUSIC/assets/font.ttf"  # Make sure font exists
        arial = ImageFont.truetype(font_path, 30)

        # Add Text Overlay
        draw = ImageDraw.Draw(background)
        draw.text((20, 20), f"{channel} | {views}", fill="white", font=arial)
        draw.text((20, 60), clear(title), fill="white", font=arial)
        draw.text((1150, 20), duration_text, fill="white", font=arial)  # Show LIVE or time

        # Save Processed Image
        os.remove(file_path)  # Delete raw image
        final_path = f"cache/{videoid}.png"
        background.save(final_path)

        return final_path  # Return final image path

    except Exception as e:
        print(f"Error processing thumbnail: {e}")
        return YOUTUBE_IMG_URL  # Return fallback on error
