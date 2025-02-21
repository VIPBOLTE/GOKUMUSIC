import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from GOKUMUSIC import app
from config import YOUTUBE_IMG_URL

def changeImageSize(maxWidth, maxHeight, image):
    return image.resize((maxWidth, maxHeight))

def truncate(text):
    words = text.split(" ")
    text1, text2 = "", ""
    for word in words:
        if len(text1) + len(word) < 30:
            text1 += " " + word
        elif len(text2) + len(word) < 30:
            text2 += " " + word
    return text1.strip(), text2.strip()

async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}_v4.png"):
        return f"cache/{videoid}_v4.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    results = VideosSearch(url, limit=1)

    try:
        response = await results.next()
        result = response["result"][0] if response and "result" in response and response["result"] else None
    except Exception as e:
        print(f"Error fetching video details: {e}")
        return YOUTUBE_IMG_URL

    if not result:
        print("Error: No results found.")
        return YOUTUBE_IMG_URL

    title = re.sub("\W+", " ", result.get("title", "Unknown Title")).title()
    duration = result.get("duration")  
    thumbnail_url = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
    views = result.get("viewCount", {}).get("short", "Unknown Views")
    channel = result.get("channel", {}).get("name", "Unknown Channel")

    # **LIVE Handling**
    is_live = duration is None
    duration_text = "🔴 LIVE" if is_live else duration

    thumbnail_path = f"cache/thumb{videoid}.png"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumbnail_path, mode="wb") as f:
                        await f.write(await resp.read())
                else:
                    print("Error: Failed to fetch thumbnail, using default.")
                    return YOUTUBE_IMG_URL
    except Exception as e:
        print(f"Exception in downloading thumbnail: {e}")
        return YOUTUBE_IMG_URL

    try:
        youtube = Image.open(thumbnail_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return YOUTUBE_IMG_URL

    background = youtube.filter(ImageFilter.BoxBlur(20)).convert("RGBA")
    background = ImageEnhance.Brightness(background).enhance(0.6)
    draw = ImageDraw.Draw(background)

    font = ImageFont.truetype("GOKUMUSIC/assets/assets/font.ttf", 30)
    title_font = ImageFont.truetype("GOKUMUSIC/assets/assets/font3.ttf", 45)

    text_x = 565
    title1, title2 = truncate(title)
    draw.text((text_x, 180), title1, fill=(255, 255, 255), font=title_font)
    draw.text((text_x, 230), title2, fill=(255, 255, 255), font=title_font)
    draw.text((text_x, 320), f"{channel}  |  {views}", fill=(255, 255, 255), font=font)

    # **LIVE or Duration Display**
    draw.text((text_x, 400), duration_text, (255, 255, 255), font=font)

    try:
        os.remove(thumbnail_path)
    except:
        pass
    background.save(f"cache/{videoid}_v4.png")
    return f"cache/{videoid}_v4.png"
