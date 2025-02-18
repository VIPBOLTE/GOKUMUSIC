import re
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardButton as Button
from GOKUMUSIC import app
from config import OWNER_ID

# Voice Chat Started
@app.on_message(filters.video_chat_started)
async def brah(_, msg: Message):
    await msg.reply("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ")

# Voice Chat Ended
@app.on_message(filters.video_chat_ended)
async def brah2(_, msg: Message):
    try:
        await msg.reply("**ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ**")
    except Exception as e:
        print(f"Error sending message: {e}")

# Invite Members on VC
@app.on_message(filters.video_chat_members_invited)
async def brah3(_, message: Message):
    text = f"{message.from_user.mention} ɪɴᴠɪᴛᴇᴅ "
    x = 0
    for user in message.video_chat_members_invited.users:
        try:
            text += f"[{user.first_name}](tg://user?id={user.id}) "
            x += 1
        except Exception as e:
            print(f"Error processing user: {e}")
    try:
        await message.reply(f"{text} 😉")
    except Exception as e:
        print(f"Error sending reply: {e}")

# Math Command
@app.on_message(filters.command("math", prefixes="/"))
async def calculate_math(_, message: Message):   
    try:
        expression = message.text.split("/math ", 1)[1]
        result = eval(expression)
        response = f"ᴛʜᴇ ʀᴇsᴜʟᴛ ɪs : {result}"
    except Exception as e:
        response = f"ɪɴᴠᴀʟɪᴅ ᴇxᴘʀᴇssɪᴏɴ\nError: {e}"
    await message.reply(response)

# Leave Group Command
@app.on_message(filters.command("leavegroup") & filters.user(OWNER_ID))
async def bot_leave(_, message: Message):
    chat_id = message.chat.id
    text = "sᴜᴄᴄᴇssғᴜʟʟʏ ʟᴇғᴛ !!."
    await message.reply_text(text)
    await app.leave_chat(chat_id=chat_id, delete=True)

# Google Search Command
@app.on_message(filters.command(["spg"], ["/", "!", "."]))
async def search(_, message: Message):
    msg = await message.reply("Searching...")
    query = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not query:
        return await msg.edit("Please provide a search query!")
    
    async with aiohttp.ClientSession() as session:
        start = 1
        async with session.get(
            f"https://content-customsearch.googleapis.com/customsearch/v1?cx=ec8db9e1f9e41e65e&q={query}&key=AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM&start={start}",
            headers={"x-referer": "https://explorer.apis.google.com"}
        ) as r:
            response = await r.json()
            result = ""

            if not response.get("items"):
                return await msg.edit("No results found!")
            
            for item in response["items"]:
                title = item["title"]
                link = item["link"]

                # Clean up links
                link = re.sub(r"\/s|\/\d|\?.*", "", link)
                if link in result:
                    continue

                result += f"{title}\n{link}\n\n"

            if not result.strip():
                return await msg.edit("No results found!")
            
            # Add next button
            prev_and_next_btns = [Button("▶️Next▶️", callback_data=f"next {start+10} {query}")]
            await msg.edit(result, disable_web_page_preview=True, reply_markup=prev_and_next_btns)
