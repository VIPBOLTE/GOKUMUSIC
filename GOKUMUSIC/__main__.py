import asyncio
import importlib
import os

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from GOKUMUSIC import LOGGER, app, userbot
from GOKUMUSIC.core.call import GOKU
from GOKUMUSIC.music import sudo
from GOKUMUSIC.plugins import ALL_MODULES
from GOKUMUSIC.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    # Ensure Render's PORT is set (for HTTP health check or similar services)
    port = int(os.getenv("PORT", 8000))

    # Ensure String Session(s) are properly set
    if not any(
        [config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]
    ):
        LOGGER(__name__).error(
            "String Session Not Filled. Please configure at least one Pyrogram session."
        )
        exit()

    # Start bot components
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("GOKUMUSIC.plugins" + all_module)
    LOGGER("GOKUMUSIC.plugins").info("All Features Loaded Successfully!")

    await userbot.start()
    await GOKU.start()

    # Attempt to stream call
    try:
        await GOKU.stream_call("https://telegra.ph/file/289cb2d7166b7e2d6c1a8.mp4")
    except NoActiveGroupCall:
        LOGGER("GOKUMUSIC").error(
            "Please start a voice chat in your log group/channel. Stopping..."
        )
        exit()
    except Exception as e:
        LOGGER("GOKUMUSIC").warning(f"Unexpected error in stream_call: {e}")

    # Log success and start idle loop
    await GOKU.decorators()
    LOGGER("GOKUMUSIC").info(
        "╔═════ஜ۩۞۩ஜ════╗\n𝗠𝗔𝗗𝗘 𝗕𝗬 𝗦𝗧𝗔𝗥𝗕𝗢𝗬\n╚═════ஜ۩۞۩ஜ════╝"
    )
    
    # Start health check server if needed (useful for Render)
    asyncio.create_task(health_check_server(port))

    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("GOKUMUSIC").info("Bot Stopped. Goodbye!")


# Health Check Server for Render
async def health_check_server(port):
    from aiohttp import web

    async def health_check(request):
        return web.Response(text="OK", status=200)

    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    LOGGER("HealthCheck").info(f"Health check server running on port {port}")
    await site.start()


import asyncio
import traceback

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(init())
    except Exception as e:
        LOGGER("GOKUMUSIC").error(f"Bot failed to start: {e}")
        LOGGER("GOKUMUSIC").error(traceback.format_exc())
