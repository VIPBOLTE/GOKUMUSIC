import time
import openai
from pyrogram import filters
from pyrogram.enums import ChatAction, ParseMode
from GOKUMUSIC import app

# Replace this with your OpenAI API key
openai.api_key = "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" # Replace with your actual OpenAI API key

# Replace this with your bot's username
BOT_USERNAME = app.me.username if app.me else "MyBot"

@app.on_message(filters.command(["chatgpt", "ai", "ask", "gpt", "solve"], prefixes=["+", ".", "/", "-", "", "$", "#", "&"]))
async def chat_gpt(bot, message):
    """Fetch a response from OpenAI's GPT-3 and reply to the user."""
    try:
        start_time = time.time()
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        # Check if the command has a query
        if len(message.command) < 2:
            return await message.reply_text(
                "Please provide a question.\n\nExample:\n`/chatgpt Where is Hastinapur?`",
                parse_mode=ParseMode.MARKDOWN
            )

        # Extract the query
        query = message.text.split(' ', 1)[1]

        # Call the OpenAI API for a response
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",  # Use "gpt-3.5-turbo" or another model if preferred
                prompt=query,
                max_tokens=150  # You can adjust the number of tokens for your needs
            )
            answer = response['choices'][0]['text'].strip()
        except openai.error.OpenAIError as e:
            return await message.reply_text(f"Error: {str(e)}")

        # Measure the response time
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)

        # Reply with the answer
        await message.reply_text(
            f"**Question:** `{query}`\n\n**Answer:** {answer}\n\nResponse time: `{response_time} ms`\n\nAnswered by: [@{BOT_USERNAME}](https://t.me/{BOT_USERNAME})",
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        await message.reply_text(f"Unexpected Error: {e}")
