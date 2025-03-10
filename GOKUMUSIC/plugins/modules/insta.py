import re
import requests
from urllib.parse import quote_plus
from pyrogram import filters
from GOKUMUSIC import app
from config import LOGGER_ID

# Primary and backup Instagram downloader APIs
INSTAGRAM_API = "https://social-dl.hazex.workers.dev/?url="
BACKUP_API = "https://insta-downloader.io/api?url="  # Example backup API

INSTAGRAM_REGEX = r"(https?://)?(www\.)?(instagram\.com|instagr\.am)/\S+"

async def fetch_instagram_video(url):
    """Attempts to fetch the video from the API, retrying if needed."""
    encoded_url = quote_plus(url)
    api_url = f"{INSTAGRAM_API}{encoded_url}"

    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.get(api_url, timeout=15)  # Increased timeout
            response.raise_for_status()
            result = response.json()

            videos = result.get("videos", [])
            if videos and videos[0].get("url"):
                return videos[0].get("url")  # Return the video URL

        except requests.exceptions.Timeout:
            print(f"⚠️ Attempt {attempt + 1}: API timed out.")
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {str(e)}")

    # If all attempts fail, try the backup API
    print("🔄 Trying the backup API...")
    backup_url = f"{BACKUP_API}{encoded_url}"
    try:
        response = requests.get(backup_url, timeout=15)
        response.raise_for_status()
        result = response.json()
        return result.get("video_url")  # Adjust this based on backup API response
    except Exception:
        return None  # No video found after retries

@app.on_message(filters.text & filters.regex(INSTAGRAM_REGEX))
async def auto_download_instagram_video(client, message):
    url = re.search(INSTAGRAM_REGEX, message.text).group(0)
    a = await message.reply_text("🔄 Fetching the video...")

    video_url = await fetch_instagram_video(url)

    if video_url:
        await a.delete()
        await message.reply_video(video_url, caption="📥 Instagram Reel Downloaded!")
    else:
        await a.edit("❌ Failed to retrieve the video. Please try again later.")
