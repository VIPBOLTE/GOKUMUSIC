from uuid import uuid4
import pyrogram
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from GOKUMUSIC import app

@app.on_message(filters.command("kang"))
async def _packkang(app, message):
    txt = await message.reply_text("Processing....")
    
    if not message.reply_to_message:
        await txt.edit("Reply to a message containing a sticker.")
        return
    
    if not message.reply_to_message.sticker:
        await txt.edit("Reply to a sticker.")
        return
    
    # Determine if the sticker is animated or not
    sticker_is_animated = message.reply_to_message.sticker.is_animated or message.reply_to_message.sticker.is_video

    # If the sticker is part of a sticker set, handle it differently
    if message.reply_to_message.sticker.set_name:
        short_name = message.reply_to_message.sticker.set_name
        stickers = await app.invoke(
            pyrogram.raw.functions.messages.GetStickerSet(
                stickerset=pyrogram.raw.types.InputStickerSetShortName(
                    short_name=short_name
                ),
                hash=0,
            )
        )
        
        # Collect stickers from the set
        shits = stickers.documents
        sticks = []
        for i in shits:
            sex = pyrogram.raw.types.InputDocument(
                id=i.id, 
                access_hash=i.access_hash, 
                file_reference=i.thumbs[0].bytes if i.thumbs else None
            )
            sticks.append(
                pyrogram.raw.types.InputStickerSetItem(
                    document=sex, emoji=i.attributes[1].alt
                )
            )
    else:
        # For single stickers, we directly add them
        sticker_document = message.reply_to_message.sticker
        file_reference = sticker_document.thumb.bytes if sticker_is_animated and sticker_document.thumb else None
        sex = pyrogram.raw.types.InputDocument(
            id=sticker_document.file_id,
            access_hash=sticker_document.file_unique_id, 
            file_reference=file_reference
        )
        sticks = [pyrogram.raw.types.InputStickerSetItem(
            document=sex, emoji=sticker_document.emoji
        )]

    # Generate a new sticker pack name using UUID
    pack_name = f"{message.from_user.first_name}_sticker_pack_by_{app.me.username}" if len(message.command) < 2 else message.text.split(maxsplit=1)[1]
    new_short_name = f"sticker_pack_{str(uuid4()).replace('-','')}_by_{app.me.username}"

    try:
        user_id = await app.resolve_peer(message.from_user.id)

        # Create the new sticker set
        await app.invoke(
            pyrogram.raw.functions.stickers.CreateStickerSet(
                user_id=user_id,
                title=pack_name,
                short_name=new_short_name,
                stickers=sticks,
            )
        )

        # Send the confirmation with the link to the newly created pack
        await txt.edit(
            f"Your sticker has been added! For fast updates, remove your pack & add again.\n🎖 ʏᴏᴜʀ ᴘᴀᴄᴋ: {len(sticks)}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "PACK", url=f"http://t.me/addstickers/{new_short_name}"
                        )
                    ]
                ]
            ),
        )
    except Exception as e:
        await message.reply(f"Error occurred: {e}")
