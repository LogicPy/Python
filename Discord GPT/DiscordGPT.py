# This Ai tool is a Discord client powered by Lollms.
# You can chat to any Ai you have loaded into your Lollms Server.
# Download Lollms here to configure your own Discord Ai bot:
# https://github.com/ParisNeo/lollms/tree/main

import discord
from discord.ext import commands, tasks
from discord import Intents
import socketio
from collections import deque
import asyncio
import re

intents = Intents.all()

# My Token ID for my bot
TOKEN = '[your API token]'  # Replace with your bot's token
PREFIX = '!'  # Command prefix, e.g., !hello

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

sio = socketio.Client()

# Global variable to store the command's context
current_ctx = None

@bot.command(name='generate')
async def generate(ctx, *, prompt: str):
    global current_ctx
    current_ctx = ctx  # Store the current message context

    # Send a "processing..." message immediately after receiving the command
    await ctx.channel.send("processing...")

    sio.emit('generate_text', {'prompt': prompt, 'personality': -1, "n_predicts": 1024})

@sio.on('text_generated')
def on_text_generated(data):
    global current_ctx

    if not current_ctx:
        return

    generated_text = data['text']
    print(generated_text)
    # Split the text into sentences using '.', '!', and '?' as delimiters
    sentences = re.split(r'[.!?]', generated_text)

    # Get the first two sentences
    first_two_sentences = '.'.join(sentences[:2]) + '.'

    # Use the stored event loop to create the task
    loop.create_task(send_generated_text(first_two_sentences))


async def send_generated_text(text):
    global current_ctx
    await current_ctx.channel.send(text)
    current_ctx = None  # Reset the context after sending the message

@bot.event
async def on_ready():
    global loop
    loop = asyncio.get_running_loop()


    print(f'{bot.user.name} has connected to Discord!')
    sio.connect('http://localhost:9600')

bot.run(TOKEN)
