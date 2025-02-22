import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL

def truncate(text):
    """Splits title into two lines."""
    words = text.split(" ")
    text1, text2 = "", ""
    for word in words:
        if len(text1) + len(word) < 30:
            text1 += " " + word
        elif len(text2) + len(word) < 30:
            text2 += " " + word
    return text1.strip(), text2.strip()

def crop_center_circle(img, output_size, border, crop_scale=1.5):
    """Creates a circular cropped thumbnail with border."""
    half_w, half_h = img.size[0] / 2, img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    img = img.crop((half_w - larger_size / 2, half_h - larger_size / 2, 
                    half_w + larger_size / 2, half_h + larger_size / 2))
    
    img = img.resize((output_size - 2 * border, output_size - 2 * border))
    final_img = Image.new("RGBA", (output_size, output_size), "white")

    mask_main = Image.new("L", (output_size - 2 * border, output_size - 2 * border), 0)
    ImageDraw.Draw(mask_main).ellipse((0, 0, output_size - 2 * border, output_size - 2 * border), fill=255)
    
    final_img.paste(img, (border, border), mask_main)

    mask_border = Image.new("L", (output_size, output_size), 0)
    ImageDraw.Draw(mask_border).ellipse((0, 0, output_size, output_size), fill=255)

    return Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)

async def get_thumb(videoid):
    """Generates a YouTube video thumbnail with overlay."""
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
    duration = result.get("duration", "🔴 LIVE")  # FIXED TypeError
    thumbnail_url = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
    views = result.get("viewCount", {}).get("short", "Unknown Views")
    channel = result.get("channel", {}).get("name", "Unknown Channel")

    thumbnail_path = f"cache/thumb{videoid}.png"
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail_url) as resp:
            if resp.status == 200:
                async with aiofiles.open(thumbnail_path, mode="wb") as f:
                    await f.write(await resp.read())

    try:
        youtube = Image.open(thumbnail_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening image: {e}")
        return YOUTUBE_IMG_URL  

    blurred_bg = youtube.filter(ImageFilter.GaussianBlur(20))
    blurred_bg = ImageEnhance.Brightness(blurred_bg).enhance(0.6)

    draw = ImageDraw.Draw(blurred_bg)
    try:
        font = ImageFont.truetype("GOKUMUSIC/assets/assets/font.ttf", 30)
        title_font = ImageFont.truetype("GOKUMUSIC/assets/assets/font3.ttf", 45)
        info_font = ImageFont.truetype("GOKUMUSIC/assets/assets/font.ttf", 25)
    except Exception as e:
        print(f"Error loading fonts: {e}")
        return YOUTUBE_IMG_URL  

    circle_thumbnail = crop_center_circle(youtube, 400, 20)
    blurred_bg.paste(circle_thumbnail, (120, 160), circle_thumbnail)

    text_x = 565
    title1, title2 = truncate(title)
    draw.text((text_x, 180), title1, fill=(255, 255, 255), font=title_font)
    draw.text((text_x, 230), title2, fill=(255, 255, 255), font=title_font)
    draw.text((text_x, 320), f"{channel}  |  {views}", fill=(255, 255, 255), font=info_font)

    progress_line_start_x = text_x
    progress_line_end_x = text_x + 580
    draw.line([progress_line_start_x, 380, progress_line_start_x + 348, 380], fill="red", width=9)
    draw.line([progress_line_start_x + 348, 380, progress_line_end_x, 380], fill="white", width=8)
    draw.ellipse([(progress_line_start_x + 348 - 5, 380 - 5), 
                  (progress_line_start_x + 348 + 5, 380 + 5)], fill="red")

    draw.text((text_x, 400), "00:00", (255, 255, 255), font=info_font)
    draw.text((1080, 400), duration, (255, 255, 255), font=info_font)  # FIXED TypeError

    try:
        play_icons = Image.open("GOKUMUSIC/assets/assets/play_icons.png").resize((580, 62))
        blurred_bg.paste(play_icons, (text_x, 450), play_icons)
    except Exception as e:
        print(f"Error opening play_icons.png: {e}")

    try:
        os.remove(thumbnail_path)
    except:
        pass

    blurred_bg.save(cached_path)
    return cached_path
