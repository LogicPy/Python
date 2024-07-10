
import discord
from discord.ext import commands
import requests
import json

# Replace 'your_token_here' with your bot's token
TOKEN = '*********************************'
PREFIX = '!'  # Command prefix, e.g., !hello

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.command(name='generate')
async def generate(ctx, *, prompt: str):
    await ctx.channel.send("processing...")

    # Define the API endpoint and headers
    api_url = "http://localhost:11434/api/chat"
    headers = {
        "Content-Type": "application/json"
    }

    # Create the JSON payload
    payload = {
        "model": "llama3",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    # Send a request to the Ollama server
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        # Print the response text for debugging
        print(response.text)
        
        # Process each line of the response
        lines = response.text.strip().split('\n')
        combined_response = ""
        for line in lines:
            try:
                data = json.loads(line)
                if 'message' in data and 'content' in data['message']:
                    combined_response += data['message']['content']
            except json.JSONDecodeError:
                continue

        await ctx.send(combined_response.strip())
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error: {e}")
    except ValueError as e:
        await ctx.send(f"JSON decode error: {e}")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
