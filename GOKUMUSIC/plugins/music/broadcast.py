import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

from GOKUMUSIC import app
from GOKUMUSIC.music import SUDOERS
from GOKUMUSIC.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from GOKUMUSIC.utils.decorators.language import language
from GOKUMUSIC.utils.formatters import alpha_to_int
from config import adminlist

IS_BROADCASTING = False


@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def broadcast_message(client, message, _):
    global IS_BROADCASTING

    if IS_BROADCASTING:
        return await message.reply_text(_["broad_9"])  # Message indicating an active broadcast.

    # Extract the message content
    if message.reply_to_message:
        reply_id = message.reply_to_message.id
        source_chat_id = message.chat.id
        broadcast_text = None
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])
        broadcast_text = message.text.split(None, 1)[1].strip()
        reply_id = None
        source_chat_id = None

    # Remove broadcast flags from text
    flags = ["-pin", "-nobot", "-pinloud", "-assistant", "-user"]
    for flag in flags:
        if flag in broadcast_text:
            broadcast_text = broadcast_text.replace(flag, "").strip()

    if not broadcast_text and not reply_id:
        return await message.reply_text(_["broad_8"])

    # Set broadcasting flag
    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])

    # Broadcast to all served chats
    await broadcast_to_chats(message, broadcast_text, reply_id, source_chat_id, _)

    # Broadcast to all users if "-user" flag is present
    if "-user" in message.text:
        await broadcast_to_users(message, broadcast_text, reply_id, source_chat_id, _)

    # Broadcast using assistants if "-assistant" flag is present
    if "-assistant" in message.text:
        await broadcast_with_assistants(message, broadcast_text, reply_id, source_chat_id, _)

    # Reset broadcasting flag
    IS_BROADCASTING = False


async def broadcast_to_chats(message, broadcast_text, reply_id, source_chat_id, _):
    chats = [int(chat["chat_id"]) for chat in await get_served_chats()]
    sent, pin_count = 0, 0

    for chat_id in chats:
        try:
            # Send or forward the message
            msg = (
                await app.forward_messages(chat_id, source_chat_id, reply_id)
                if reply_id
                else await app.send_message(chat_id, text=broadcast_text)
            )

            # Pin message if required
            if "-pin" in message.text:
                await msg.pin(disable_notification=True)
                pin_count += 1
            elif "-pinloud" in message.text:
                await msg.pin(disable_notification=False)
                pin_count += 1

            sent += 1
            await asyncio.sleep(0.2)  # To avoid hitting rate limits
        except FloodWait as fw:
            await handle_flood_wait(fw)
        except Exception as e:
            print(f"Failed to send message to chat {chat_id}: {e}")

    # Send a summary to the broadcaster
    await message.reply_text(_["broad_3"].format(sent, pin_count))


async def broadcast_to_users(message, broadcast_text, reply_id, source_chat_id, _):
    users = [int(user["user_id"]) for user in await get_served_users()]
    sent = 0

    for user_id in users:
        try:
            await app.forward_messages(user_id, source_chat_id, reply_id) if reply_id else await app.send_message(
                user_id, text=broadcast_text
            )
            sent += 1
            await asyncio.sleep(0.2)
        except FloodWait as fw:
            await handle_flood_wait(fw)
        except Exception as e:
            print(f"Failed to send message to user {user_id}: {e}")

    # Send a summary to the broadcaster
    await message.reply_text(_["broad_4"].format(sent))


async def broadcast_with_assistants(message, broadcast_text, reply_id, source_chat_id, _):
    from GOKUMUSIC.core.userbot import assistants

    summary = _["broad_6"]
    for num, assistant in enumerate(assistants, start=1):
        sent = 0
        client = await get_client(assistant)

        async for dialog in client.get_dialogs():
            try:
                await client.forward_messages(dialog.chat.id, source_chat_id, reply_id) if reply_id else await client.send_message(
                    dialog.chat.id, text=broadcast_text
                )
                sent += 1
                await asyncio.sleep(3)
            except FloodWait as fw:
                await handle_flood_wait(fw)
            except Exception as e:
                print(f"Assistant {assistant} failed in chat {dialog.chat.id}: {e}")

        summary += _["broad_7"].format(num, sent)

    # Edit the initial message with the broadcast summary
    await message.reply_text(summary)


async def handle_flood_wait(fw):
    wait_time = fw.value
    if wait_time > 200:
        print(f"Skipping due to long FloodWait: {wait_time}s")
    else:
        print(f"FloodWait encountered: {wait_time}s. Sleeping...")
        await asyncio.sleep(wait_time)


# Auto-clean admin list
async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except Exception as e:
            print(f"Error in auto_clean: {e}")


asyncio.create_task(auto_clean())
