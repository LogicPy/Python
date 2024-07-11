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

# Dictionary to store user context
user_context = {}

@bot.command(name='generate')
async def generate(ctx, *, prompt: str):
    await ctx.channel.send("processing...")

    user_id = str(ctx.author.id)
    
    # Retrieve the context for the user
    context = user_context.get(user_id, "")
    
    # Update the context with the new prompt
    context += f" User: {prompt}\n"
    
    # Define the API endpoint and headers
    api_url = "http://localhost:11434/api/chat"
    headers = {
        "Content-Type": "application/json"
    }

    # Create the JSON payload with context
    payload = {
        "model": "llama3",
        "messages": [
            {
                "role": "system",
                "content": "You are a role-playing AI. Your name is Thea and you are talking to a user at the mall."
            },
            {
                "role": "user",
                "content": context
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

        # Update the context with the AI's response
        context += f" AI: {combined_response.strip()}\n"
        user_context[user_id] = context

        await ctx.send(combined_response.strip())
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error: {e}")
    except ValueError as e:
        await ctx.send(f"JSON decode error: {e}")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
