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

async def download_image(url, path):
    """Downloads an image from the URL and saves it."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(path, mode="wb") as f:
                        await f.write(await resp.read())
                    return path
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None  

async def get_thumb(videoid):
    """Fetches video thumbnail and generates an image with overlay."""
    cached_path = f"cache/{videoid}_v4.png"
    if os.path.isfile(cached_path):
        return cached_path

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

    # LIVE Handling
    is_live = duration is None
    duration_text = "🔴 LIVE" if is_live else duration

    thumbnail_path = f"cache/thumb{videoid}.png"
    
    # **Thumbnail Download with Fallback**
    downloaded_path = await download_image(thumbnail_url, thumbnail_path)
    if not downloaded_path:  
        print("Thumbnail fetch failed! Using default YouTube image.")
        downloaded_path = await download_image(YOUTUBE_IMG_URL, thumbnail_path)

    try:
        youtube = Image.open(downloaded_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return YOUTUBE_IMG_URL

    # **Blurred Background**
    blurred_background = youtube.convert("RGBA").filter(ImageFilter.GaussianBlur(20))
    blurred_background = ImageEnhance.Brightness(blurred_background).enhance(0.6)
    
    # **Creating HD Circular Thumbnail**
    circle_size = 350  # Adjust size of the circle
    hd_thumbnail = youtube.resize((circle_size, circle_size), Image.ANTIALIAS)
    
    # Create a circular mask for HD image
    circle_mask = Image.new("L", (circle_size, circle_size), 0)
    draw_mask = ImageDraw.Draw(circle_mask)
    draw_mask.ellipse((0, 0, circle_size, circle_size), fill=255)
    
    # Apply the mask to the HD thumbnail
    hd_thumbnail.putalpha(circle_mask)

    # **Draw Text on Image**
    draw = ImageDraw.Draw(blurred_background)
    font = ImageFont.truetype("GOKUMUSIC/assets/assets/font.ttf", 30)
    title_font = ImageFont.truetype("GOKUMUSIC/assets/assets/font3.ttf", 45)

    text_x = 565
    title1, title2 = truncate(title)
    draw.text((text_x, 180), title1, fill=(255, 255, 255), font=title_font)
    draw.text((text_x, 230), title2, fill=(255, 255, 255), font=title_font)
    draw.text((text_x, 320), f"{channel}  |  {views}", fill=(255, 255, 255), font=font)

    # LIVE or Duration Display
    draw.text((text_x, 400), duration_text, (255, 255, 255), font=font)

    # **Paste HD Circle on Right Side**
    hd_position = (blurred_background.width - circle_size - 50, 100)  # Adjust position
    blurred_background.paste(hd_thumbnail, hd_position, hd_thumbnail)

    # **Overlay the thum.png**
    try:
        thum_overlay = Image.open("GOKUMUSIC/assets/thum.png").convert("RGBA")
        thum_overlay = thum_overlay.resize((blurred_background.width, blurred_background.height), Image.ANTIALIAS)
        blurred_background.paste(thum_overlay, (0, 0), thum_overlay)  # Overlay thum.png
    except Exception as e:
        print(f"Error opening thum.png overlay: {e}")
    
    # Save the final image with overlay
    try:
        os.remove(thumbnail_path)
    except:
        pass
    blurred_background.save(cached_path)
    return cached_path
