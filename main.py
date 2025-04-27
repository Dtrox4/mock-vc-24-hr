import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import asyncio
import threading

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
TOKEN = os.getenv('DISCORD_TOKEN')

# Define the intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
intents.voice_states = True      # Enable voice state intents

# Create a bot instance with command prefix '!' and the specified intents
bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}!')

@bot.command()
async def joinvc(ctx, channel_id: int):
    # Get the channel by ID
    channel = bot.get_channel(channel_id)
    if channel and isinstance(channel, discord.VoiceChannel):
        # Join the voice channel
        await channel.connect()
        await ctx.send(f'Joined {channel.name}!')
    else:
        await ctx.send('Invalid channel ID or not a voice channel.')

# Create a Flask app
app = Flask(__name__)
# Run the bot in a separate thread
def run_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(port=5000)

@app.route('/joinvc', methods=['POST'])
def join_voice_channel():
    data = request.json
    channel_id = data.get('channel_id')

    if channel_id:
        # Trigger the joinvc command
        channel = bot.get_channel(channel_id)
        if channel and isinstance(channel, discord.VoiceChannel):
            asyncio.run(channel.connect())
            return jsonify({'message': f'Bot joined {channel.name}!'}), 200
        else:
            return jsonify({'error': 'Invalid channel ID or not a voice channel.'}), 400
    return jsonify({'error': 'Channel ID is required.'}), 400

@bot.command()
async def react(ctx, message_id: int, emoji: str):
    """React to a message with a specified emoji."""
    try:
        # Fetch the message using the message ID
        message = await ctx.channel.fetch_message(message_id)
        
        # Add the reaction
        await message.add_reaction(emoji)
        await ctx.send(f"Reacted to message ID {message_id} with {emoji}!")
    except discord.NotFound:
        await ctx.send("Message not found. Please check the message ID.")
    except discord.HTTPException:
        await ctx.send("Failed to add reaction. Please check the emoji or try again.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Make sure to add this command to your bot's command processing
@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore messages from bots

    await bot.process_commands(message)
