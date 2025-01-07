import config
import asyncio
from datetime import datetime, timedelta
from pyrogram.raw import types
from GOKUMUSIC.utils.database import is_cleanmode_on, set_queries
from GOKUMUSIC import app

AUTO_DELETE = config.CLEANMODE_DELETE_MINS
cleanmode_group = 15
clean = {}

@app.on_raw_update(group=cleanmode_group)
async def clean_mode(client, update, users, chats):
    if not isinstance(update, types.UpdateReadChannelOutbox):
        return
    if users or chats:
        return
    message_id = update.max_id
    chat_id = int(f"-100{update.channel_id}")
    
    # Check if clean mode is on for the chat
    if not await is_cleanmode_on(chat_id):
        return

    if chat_id not in clean:
        clean[chat_id] = []

    # Calculate time to delete the message after AUTO_DELETE minutes
    time_now = datetime.now()
    put = {
        "msg_id": message_id,
        "timer_after": time_now + timedelta(minutes=AUTO_DELETE),
    }
    clean[chat_id].append(put)

    await set_queries(1)

async def auto_clean():
    while True:
        await asyncio.sleep(config.AUTO_SLEEP)
        try:
            # Check for chats that have messages to clean
            for chat_id in clean:
                if chat_id == config.LOG_GROUP_ID:
                    continue
                for x in clean[chat_id]:
                    if datetime.now() > x["timer_after"]:
                        try:
                            await app.delete_messages(
                                chat_id, x["msg_id"]
                            )
                        except FloodWait as e:
                            await asyncio.sleep(e.x)
                        except:
                            continue
                    else:
                        continue
        except Exception:
            continue
