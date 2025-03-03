import os
import random
from datetime import datetime
from telegraph import upload_file
from PIL import Image, ImageDraw
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType

# Import the bot instance
from GOKUMUSIC import app as app  

# Define Keyboard
POLICE = [
    [
        InlineKeyboardButton(
            text="𓊈𝗚𝗢𝗞𝗨 𝗕𝗢𝗧 𝗠𝗔𝗞𝗘𝗥𓊉",
            url="https://t.me/goku_groupz",
        ),
    ],
]

# Date Functions
def dt():
    now = datetime.now()
    return now.strftime("%d/%m/%Y"), now.strftime("%H:%M")

def dt_tom():
    today, _ = dt()
    day, month, year = map(int, today.split("/"))
    return f"{day+1}/{month}/{year}"

tomorrow = dt_tom()
today = dt()[0]

@app.on_message(filters.command("couples"))
async def ctest(_, message):
    cid = message.chat.id

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command only works in groups.")

    msg = await message.reply_text("Generating couples image...")

    # Get list of users (excluding bots)
    list_of_users = [
        i.user.id async for i in app.get_chat_members(message.chat.id, limit=50) if not i.user.is_bot
    ]

    if len(list_of_users) < 2:
        return await msg.edit("Not enough users in the group to form a couple.")

    # Randomly select two unique users
    c1_id, c2_id = random.sample(list_of_users, 2)

    # Get profile pictures
    try:
        p1 = await app.download_media((await app.get_chat(c1_id)).photo.big_file_id, file_name=f"pfp1_{cid}.png")
    except:
        p1 = "assets/default.png"  # Fallback image

    try:
        p2 = await app.download_media((await app.get_chat(c2_id)).photo.big_file_id, file_name=f"pfp2_{cid}.png")
    except:
        p2 = "assets/default.png"

    # Open images and process
    img1, img2 = Image.open(p1).resize((437, 437)), Image.open(p2).resize((437, 437))
    
    # Create circular masks
    mask = Image.new('L', img1.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img1.size, fill=255)

    img1.putalpha(mask)
    img2.putalpha(mask)

    # Merge into template
    img = Image.open("assets/cppic.png")
    img.paste(img1, (116, 160), img1)
    img.paste(img2, (789, 160), img2)
    img.save(f"couple_{cid}.png")

    # Get user mentions
    N1, N2 = (await app.get_users(c1_id)).mention, (await app.get_users(c2_id)).mention

    # Send result
    caption = f"**Today's Couple of the Day:**\n\n{N1} + {N2} = ❤️💖\n\nNext couples will be selected on {tomorrow}!"
    await message.reply_photo(f"couple_{cid}.png", caption=caption, reply_markup=InlineKeyboardMarkup(POLICE))
    await msg.delete()

    # Upload to Telegraph
    try:
        uploaded_files = upload_file(f"couple_{cid}.png")
        telegraph_url = "https://graph.org/" + uploaded_files[0]
        print(f"Uploaded Image URL: {telegraph_url}")
    except Exception as e:
        print(f"Error uploading to Telegraph: {e}")

    # Clean up files
    os.remove(f"couple_{cid}.png")
    if os.path.exists(p1):
        os.remove(p1)
    if os.path.exists(p2):
        os.remove(p2)

__mod__ = "COUPLES"
__help__ = """
**» /couples** - Get today's selected couples in an interactive image view.
"""
