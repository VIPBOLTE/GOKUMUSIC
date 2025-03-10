import requests
import os
from pyrogram import filters
from GOKUMUSIC import app

# Function to upload a file to envs.sh
def upload_to_envs(file_path=None, file_url=None, expires=None, secret=None):
    url = "https://envs.sh"
    files = {}
    data = {}
    
    # If uploading a local file
    if file_path:
        files = {'file': open(file_path, 'rb')}
    
    # If uploading a remote URL
    elif file_url:
        data = {'url': file_url}
    
    # Add secret and expiration if provided
    if secret:
        data['secret'] = secret
    if expires:
        data['expires'] = expires  # Expiration time in hours
    
    # Make the request
    response = requests.post(url, files=files, data=data)
    
    # Close file after the upload
    if file_path:
        files['file'].close()
    
    if response.status_code == 200:
        print("File uploaded successfully to envs.sh!")
        print("File URL:", response.text.strip())
        return response.text.strip()
    else:
        print("Failed to upload file to envs.sh.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return None

# Function to upload a file to Catbox
def upload_to_catbox(file_path):
    url = "https://catbox.moe/user/api.php"
    with open(file_path, "rb") as file:
        response = requests.post(
            url,
            data={"reqtype": "fileupload"},
            files={"fileToUpload": file}
        )
        if response.status_code == 200 and response.text.startswith("https"):
            print("Image uploaded successfully to Catbox!")
            return response.text
        else:
            raise Exception(f"Error uploading to Catbox: {response.text}")

# Function to upload a file to 0x0
def upload_to_0x0(file_path):
    url = "https://0x0.st"
    with open(file_path, "rb") as file:
        response = requests.post(url, files={"file": file})
        if response.status_code == 200:
            print("File uploaded successfully to 0x0!")
            return response.text.strip()
        else:
            raise Exception(f"Error uploading to 0x0: {response.text}")

# Pyrogram handler for the /tgm command
@app.on_message(filters.command("tgm") & filters.reply)
async def send_catbox_and_envs_link(client, message):
    reply = message.reply_to_message
    if reply and (reply.photo or reply.document):  # Check if the replied message contains a photo or document
        try:
            # Send processing message
            processing_message = await message.reply("Processing... Please wait.")
            
            # Download the replied media
            path = await reply.download()
            
            # Check if the file is a PNG, JPG, JPEG, GIF, PDF, or DOCX
            if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.pdf', '.docx')):
                # Initialize success flags for each service
                catbox_url = envs_url = x0_url = None
                
                # Upload the file to Catbox
                try:
                    catbox_url = upload_to_catbox(path)
                except Exception:
                    catbox_url = "This link could not be created for Catbox."

                # Upload the file to envs.sh
                try:
                    envs_url = upload_to_envs(file_path=path, expires=24, secret="mysecret123")
                except Exception:
                    envs_url = "This link could not be created for Env.sh."
                
                # Upload the file to 0x0
                try:
                    x0_url = upload_to_0x0(path)
                except Exception:
                    x0_url = "This link could not be created for 0x0."

                # Send both links to the user
                await message.reply(
                    text=f"Yᴏᴜʀ ʟɪɴᴋs sᴜᴄᴄᴇssғᴜʟ Gᴇɴ:\n\n"
                         f"1. Catbox Link: \n{catbox_url}\n\n"
                         f"2. Env sh Link: \n{envs_url}\n\n"
                         f"3. 0x0 Link: \n{x0_url}"
                )
                
                # Delete the processing message after the links are sent
                await processing_message.delete()
            else:
                await message.reply("Please reply to a valid image (PNG, JPG, etc.) or document (PDF, DOCX).")
        except Exception as e:
            await message.reply(f"Failed to upload file. Error: {str(e)}")
        finally:
            # Ensure cleanup of the downloaded file
            if os.path.exists(path):
                os.remove(path)
    else:
        await message.reply("Please reply to a photo or a document.")
