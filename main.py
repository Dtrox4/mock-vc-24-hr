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

# Run the bot in a separate thread
def run_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(port=5000)
