import os
import re
import random

import aiofiles
import aiohttp

from PIL import Image, ImageDraw, ImageEnhance
from PIL import ImageFilter, ImageFont, ImageOps

from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from GOKUMUSIC import app
from config import YOUTUBE_IMG_URL

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def clear(text):
    list = text.split(" ")
    title = ""
    for i in list:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()

async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"

            # Check if duration is None
            duration = result.get("duration", "Unknown Mins")  # Default if None
            
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            
            views = result.get("viewCount", {}).get("short", "Unknown Views")  # Default if None
            channel = result.get("channel", {}).get("name", "Unknown Channel")  # Default if None

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # Check if img is None or invalid (e.g., failed to download thumbnail)
        try:
            youtube = Image.open(f"cache/thumb{videoid}.png")
        except Exception as e:
            print(f"Error opening image: {e}")
            return YOUTUBE_IMG_URL  # Return fallback URL if image fails to load

        # If image is valid, proceed with image processing
        colors = ["white", "red", "orange", "yellow", "green", "cyan", "azure", "blue", "violet", "magenta", "pink"]
        border = random.choice(colors)
        image1 = changeImageSize(1280, 720, youtube)
        bg_bright = ImageEnhance.Brightness(image1)
        bg_logo = bg_bright.enhance(1.1)
        bg_contra = ImageEnhance.Contrast(bg_logo)
        bg_logo = bg_contra.enhance(1.1)
        logox = ImageOps.expand(bg_logo, border=7, fill=f"{border}")
        background = changeImageSize(1280, 720, logox)
        
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
    except Exception as e:
        print(f"Error processing thumbnail: {e}")
        return YOUTUBE_IMG_URL  # Return fallback image URL if there is any exception
