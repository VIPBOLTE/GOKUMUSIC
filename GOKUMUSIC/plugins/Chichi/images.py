import logging
import aiohttp
from pyrogram import filters
from pyrogram.types import InputMediaPhoto
from GOKUMUSIC import app

# Set up logging
logging.basicConfig(level=logging.INFO)

PEXELS_API_KEY = "Dg5JON257csUvwsIN8dgnGEqxoxhfheabvbu7fhRnpilvCDe0JZQWbcA"  # Replace with your Pexels API key
PEXELS_BASE_URL = "https://api.pexels.com/v1/search"

class ImageSearchClient:
    """Handles API requests to the Pexels image search service."""
    
    def __init__(self):
        self.api_key = PEXELS_API_KEY
        self.session = aiohttp.ClientSession()

    async def search_images(self, query, per_page=6):
        """
        Fetch images from the Pexels API for a given query.
        
        Args:
            query (str): The search term provided by the user.
            per_page (int): Number of images to fetch.
        
        Returns:
            dict: The API response containing image URLs or None if the request fails.
        """
        headers = {"Authorization": self.api_key}
        params = {"query": query, "per_page": per_page}

        try:
            async with self.session.get(PEXELS_BASE_URL, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logging.error(f"Invalid status code {response.status} from API.")
                    return None
        except Exception as e:
            logging.error(f"Error while fetching images: {str(e)}")
            return None

    async def close(self):
        """Closes the aiohttp session."""
        await self.session.close()

async def fetch_and_send_images(message, query):
    """
    Fetch images from the API and send them to the chat.
    
    Args:
        message (pyrogram.types.Message): The Pyrogram message object.
        query (str): The search term provided by the user.
    """
    client = ImageSearchClient()

    # Get images from Pexels API
    images = await client.search_images(query)

    if not images or "photos" not in images or not images["photos"]:
        await message.reply("No images found for the given query.")
        await client.close()
        return

    # Prepare the media group to send images
    media_group = []
    count = 0
    msg = await message.reply("Fetching images from Pexels...")

    for photo in images["photos"][:6]:  # Limit to the first 6 images
        media_group.append(InputMediaPhoto(media=photo["src"]["medium"]))  # Use medium-sized images
        count += 1
        await msg.edit(f"=> Scraped {count} image(s)")

    # Send the images in a media group
    try:
        await app.send_media_group(
            chat_id=message.chat.id,
            media=media_group,
            reply_to_message_id=message.id
        )
        await msg.delete()  # Delete the "Fetching images..." message
    except Exception as e:
        await msg.delete()
        logging.error(f"Error sending media group: {str(e)}")
        await message.reply(f"Error: {str(e)}")
    
    await client.close()

@app.on_message(filters.command(["image"], prefixes=["/", "!", "%", ",", ".", "@", "#"]))
async def image_search(_, message):
    """
    Command handler for the `/image` command.
    Extracts the query from the message and fetches images.
    
    Args:
        message (pyrogram.types.Message): The Pyrogram message object.
    """
    try:
        query = message.text.split(None, 1)[1].strip()  # Extract query after the command
        if not query:
            raise IndexError  # Trigger exception if query is empty
    except IndexError:
        return await message.reply("Please provide an image name to search 🔍")

    # Fetch and send images for the given query
    await fetch_and_send_images(message, query)
