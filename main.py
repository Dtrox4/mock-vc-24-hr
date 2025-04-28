import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import asyncio
from threading import Thread

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
TOKEN = os.getenv('DISCORD_TOKEN')

# Replace with your Discord User ID
YOUR_USER_ID = 1212229549459374222

# Authorized users
AUTHORIZED_USERS = {YOUR_USER_ID, 845578292778238002, 1177672910102614127, 1305007578857869403, 1147059630846005318}

# Define the intents
intents = discord.Intents.default()
intents = discord.Intents.default()
intents.reactions = True
intents.messages = True
intents.message_content = True
intents.voice_states = True      # Enable voice state intents

# Create a bot instance with command prefix '!' and the specified intents
bot = commands.Bot(command_prefix='.', intents=intents)

message_id_to_listen = None

app = Flask(__name__)
@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}!')

@bot.command()
async def listenreactions(ctx, message_id: int):
    global message_id_to_listen
    message_id_to_listen = message_id
    await ctx.send(f'Now listening for reactions on message ID: {message_id}')

@bot.event
async def on_reaction_remove(reaction, user):
    # Ignore bot reactions
    if user.bot:
        return

    # Only react if it's the right message
    if reaction.message.id == message_id_to_listen:
        # Fetch the full updated message
        try:
            message = await reaction.message.channel.fetch_message(reaction.message.id)
        except discord.NotFound:
            print(f"Message {reaction.message.id} not found.")
            return
        except discord.HTTPException as e:
            print(f"HTTP Error fetching message: {e}")
            return

        # Check if all reactions are empty (only bot or none left)
        all_empty = all(r.count <= 1 for r in message.reactions)

        if all_empty:
            embed = discord.Embed(
                title="All Reactions Cleared",
                description=f"All reactions have been cleared from the message by {user.mention}.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Message ID: {reaction.message.id}")

            channel_id = 1365929942235222017  # Your target channel ID
            channel = bot.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    print(f"Cannot send message to channel ID: {channel_id}")
                except discord.HTTPException as e:
                    print(f"HTTP error sending to channel ID: {channel_id} — {e}")

                    

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
async def leavevc(ctx):
    """Leave the voice channel."""
    if ctx.voice_client:  # Check if the bot is connected to a voice channel
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I am not in a voice channel!")

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

bot.run(TOKEN)


