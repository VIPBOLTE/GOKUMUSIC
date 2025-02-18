from pyrogram import Client, filters, types as t
from lexica import Client as ApiClient, AsyncClient
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from math import ceil
import asyncio

# Initialize API Client
api = ApiClient()
Models = api.getModels()  # Fetch models from the API
Database = {}  # Temporary in-memory database for user prompts


async def ImageGeneration(model_id, prompt):
    """Generate an image using the specified model and prompt."""
    try:
        async with AsyncClient() as client:
            output = await client.generate(model_id, prompt, "")
            if output.get('code') != 1:
                return None
            if output.get('code') == 69:  # NSFW content detected
                return "NSFW"

            task_id, request_id = output['task_id'], output['request_id']
            await asyncio.sleep(20)

            for _ in range(15):  # Retry up to 15 times
                response = await client.getImages(task_id, request_id)
                if response.get('code') == 2:
                    return response['img_urls']  # Return generated images
                await asyncio.sleep(5)
            return None
    except Exception as e:
        raise Exception(f"Image generation failed: {e}")


def getText(message):
    """Extract the text after the command."""
    if message.text:
        parts = message.text.split(maxsplit=1)
        return parts[1] if len(parts) > 1 else None
    return None


def paginate_models(page_n: int, models: list, user_id: int):
    """Paginate the list of models into inline keyboard buttons."""
    buttons = [
        InlineKeyboardButton(model['name'], callback_data=f"d.{model['id']}.{user_id}")
        for model in models
    ]
    pairs = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

    if len(pairs) > 3:
        pairs.append([
            InlineKeyboardButton("◁", callback_data=f"d.left.{page_n}.{user_id}"),
            InlineKeyboardButton("⌯ Cancel ⌯", callback_data="close_data"),
            InlineKeyboardButton("▷", callback_data=f"d.right.{page_n}.{user_id}"),
        ])
    else:
        pairs.append([
            InlineKeyboardButton("⌯ Back ⌯", callback_data=f"d.-1.{user_id}")
        ])
    
    return pairs


@app.on_message(filters.command(["draw", "create", "imagine", "dream"]))
async def draw(_, message: t.Message):
    """Handle the /draw command."""
    global Database
    prompt = getText(message)
    if not prompt:
        return await message.reply_text("Please provide a prompt.\nUsage: `/draw <prompt>`")

    user_id = message.from_user.id
    Database[user_id] = {'prompt': prompt, 'reply_to_id': message.id}
    buttons = paginate_models(0, Models, user_id)

    await message.reply_text(
        f"Hello {message.from_user.mention}!\n\nSelect your image generator model:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(r"^d\.(.*)"))
async def select_model(_, query: t.CallbackQuery):
    """Handle model selection from inline keyboard."""
    global Database
    data = query.data.split('.')
    action = data[1]
    user_id = int(data[-1])

    if query.from_user.id != user_id:
        return await query.answer("You are not authorized to perform this action.", show_alert=True)

    if action in {"right", "left"}:
        current_page = int(data[2])
        new_page = current_page + 1 if action == "right" else current_page - 1
        buttons = paginate_models(new_page, Models, user_id)
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
        return

    if action == "-1":  # Back button
        await query.edit_message_text("Prompt selection canceled.")
        Database.pop(user_id, None)
        return

    model_id = int(action)
    user_data = Database.get(user_id)

    if not user_data:
        return await query.edit_message_text("Something went wrong. Please try again.")

    await query.edit_message_text("Generating your image, please wait...")
    prompt = user_data['prompt']
    img_urls = await ImageGeneration(model_id, prompt)

    if not img_urls:
        return await query.edit_message_text("Failed to generate the image. Please try again.")
    if img_urls == "NSFW":
        return await query.edit_message_text("NSFW content is not allowed!")

    media_group = [
        InputMediaPhoto(url, caption=f"Your Prompt:\n`{prompt}`") if i == len(img_urls) - 1 else InputMediaPhoto(url)
        for i, url in enumerate(img_urls)
    ]

    await query.message.delete()
    Database.pop(user_id, None)

    await _.send_media_group(
        chat_id=query.message.chat.id,
        media=media_group,
        reply_to_message_id=user_data['reply_to_id']
    )
