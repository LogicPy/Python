import discord
from discord.ext import commands
import requests
import json
import os
import json
import asyncio
import logging
from typing import Optional, Dict

import discord
from discord.ext import commands
import aiohttp
from dotenv import load_dotenv

# Load environment variables from a .env file (ensure this file is in your .gitignore)
load_dotenv()

# -----------------------------
# Configuration and Constants
# -----------------------------

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("discord_gpt_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Environment Variables
TOKEN = os.getenv('DISCORD_TOKEN')

API_URL = os.getenv('API_URL', 'http://localhost:11434/api/chat')  # Default to localhost if not set

# Define intents (ensure 'message_content' intent is enabled in Discord Developer Portal)
intents = discord.Intents.default()
intents.message_content = True

# Create a bot instance with the defined intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store user context
user_context: Dict[str, str] = {}

# -----------------------------
# Helper Functions
# -----------------------------

async def fetch_ai_response(context: str) -> Optional[str]:
    """
    Sends the user context to the AI API and retrieves the response.

    Args:
        context (str): The conversation context.

    Returns:
        Optional[str]: The AI's response or None if an error occurred.
    """
    payload = {
        "model": "dolphin-llama3",
        "messages": [
            {
                "role": "system",
                "content": "You are a role-playing AI. Your name is Jarvis, but you're a much different more comedic and high energy Jarvis than Tony Stark's personal ai.."
            },
            {
                "role": "user",
                "content": context
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                response_text = await resp.text()
                logger.debug(f"AI API Response: {response_text}")

                # Assuming the API returns JSON lines
                lines = response_text.strip().split('\n')
                combined_response = ""
                for line in lines:
                    try:
                        data = json.loads(line)
                        if 'message' in data and 'content' in data['message']:
                            combined_response += data['message']['content']
                    except json.JSONDecodeError:
                        logger.warning("Received a non-JSON response line.")
                        continue

                return combined_response.strip()

    except aiohttp.ClientError as e:
        logger.error(f"HTTP request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


def update_user_context(user_id: str, user_message: str, ai_response: str):
    """
    Updates the conversation context for a user.

    Args:
        user_id (str): The Discord user ID.
        user_message (str): The latest message from the user.
        ai_response (str): The AI's response to the user's message.
    """
    context = user_context.get(user_id, "")
    context += f"User: {user_message}\nAI: {ai_response}\n"
    user_context[user_id] = context
    logger.debug(f"Updated context for user {user_id}.")

# -----------------------------
# Event Handlers
# -----------------------------

@bot.event
async def on_ready():
    """
    Event handler triggered when the bot is ready.
    """
    logger.info(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    """
    Event handler triggered on every message in the server.
    The bot responds to any message directed at it or mentions.
    """
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    user_message = message.content.lower().strip()  # Clean up and lower-case the user message
    user_id = str(message.author.id)

    # Use typing indicator for text channels and DM channels
    async with message.channel.typing():
        # If the message doesn't start with '!', assume it's a regular message meant for AI processing
        if not user_message.startswith('!'):
            await message.channel.send("Processing your request...")

            # Retrieve the context for the user
            context = user_context.get(user_id, "")
            context += f"User: {message.content}\n"

            # Send the message to the AI and get the response
            ai_response = await fetch_ai_response(context)

            if ai_response:
                # If AI gives a response, send it and update context
                context += f"AI: {ai_response}\n"
                user_context[user_id] = context
                await message.channel.send(ai_response)
            else:
                # If AI fails to provide a response, send the fallback message
                await message.channel.send("I'm here to help! Type `!help` to see what I can do.")

    # Ensure commands (like !help, !reset) are processed as well
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    """
    Global error handler for commands.

    Args:
        ctx (discord.Context): The context in which the error occurred.
        error (commands.CommandError): The exception raised.
    """
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, I didn't understand that command. Use `!help` to see available commands.")
    else:
        await ctx.send("An error occurred while processing the command.")
        logger.error(f"Error in command '{ctx.command}': {error}")

# -----------------------------
# Bot Commands
# -----------------------------

@bot.command(name='custom_help', help='Displays available commands.')
async def help_command(ctx):
    """
    Handles the !custom_help command to display available commands.

    Args:
        ctx (discord.Context): The context in which the command was invoked.
    """
    help_message = (
        "📜 **Available Commands:**\n\n"
        "`!custom_help` - Display this help message.\n"
        "`!reset` - Reset your conversation context.\n"
        "📌 **Direct Messaging:**\n"
        "Mention me in any channel with your message, and I'll respond accordingly."
    )
    await ctx.send(help_message)
    logger.info(f"Displayed custom help message to user {ctx.author}.")

@bot.command(name='reset', help='Resets your conversation context.')
async def reset_command(ctx):
    """
    Handles the !reset command to clear the user's conversation context.

    Args:
        ctx (discord.Context): The context in which the command was invoked.
    """
    user_id = str(ctx.author.id)
    user_context.pop(user_id, None)
    await ctx.send("Your conversation context has been reset.")
    logger.info(f"Reset conversation context for user {ctx.author}.")

# -----------------------------
# Running the Bot
# -----------------------------

def main():
    """
    Main function to run the Discord bot.
    """
    if not TOKEN:
        logger.error("DISCORD_TOKEN is not set. Please set it in the environment variables.")
        return

    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Failed to run the bot: {e}")

if __name__ == "__main__":
    main()
