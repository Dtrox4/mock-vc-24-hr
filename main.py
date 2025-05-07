import discord
from discord.ext import commands
import os
import re
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import asyncio
from threading import Thread
from goodboy_punisher import handle_punishment, toggle_punishment_mode, get_mode

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
TOKEN = os.getenv('DISCORD_TOKEN')

YOUR_USER_ID = {
    1212229549459374222,
    845578292778238002,
    1238152637959110679
}

AUTHORIZED_USERS = {
    1212229549459374222,
    845578292778238002,
    1177672910102614127,
    1305007578857869403,
    1147059630846005318
}

TRIGGER_KEYWORDS = re.compile(r"\b(good\s?boy|gboy|goodboy)\b", re.IGNORECASE)
TARGET_USER_IDS = {1212229549459374222, 845578292778238002}
WHITELIST_USER_IDS = {1305007578857869403, 1212229549459374222, 845578292778238002, 1177672910102614127}
JAIL_ROLE_ID = 1359325650380652654

# Define channels and optional messages
WELCOME_CHANNELS = {
    1359328373356363987: None,
    1360104912939257978: None,
    1366327489122668644: None,
    1359319883988336924: "welc! rep **/mock** 4 pic, bst for roles!"  # Add a custom message here
}

AUTO_KICK_USERS = set()

# Users being skulled
user_skull_list = set()

# Define the intents
intents=discord.Intents.all()
intents.reactions = True
intents.messages = True
intents.message_content = True
intents.voice_states = True      # Enable voice state intents

# Create a bot instance with command prefix '!' and the specified intents
bot = commands.Bot(command_prefix=commands.when_mentioned_or('.'), intents=discord.Intents.all())

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
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.streaming,
        name=".gg/mock active giveaways!",
        url="https://twitch.tv/your_channel"
    ))

@bot.event
async def on_member_join(member):
    for channel_id, custom_message in WELCOME_CHANNELS.items():
        channel = member.guild.get_channel(channel_id)
        if channel:
            if custom_message:
                content = f"{member.mention} {custom_message}"
            else:
                content = f"{member.mention}"
            await channel.send(content, delete_after=30)

    if member.id in AUTO_KICK_USERS:
        try:
            await member.kick(reason="Auto-kick: flagged user ID")
            print(f"Kicked {member} ({member.id}) on join.")
        except discord.Forbidden:
            print(f"Permission error while kicking {member}.")
        except discord.HTTPException as e:
            print(f"HTTP error while kicking {member}: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id in user_skull_list:
        try:
            await message.add_reaction("☠️")
        except discord.Forbidden:
            print(f"Missing permissions to react in {message.channel.name}")
        except discord.HTTPException as e:
            print(f"Failed to add reaction: {e}")

    if (
        message.reference
        and message.reference.resolved
        and message.reference.resolved.author.id in TARGET_USER_IDS
        and message.author.id not in WHITELIST
    ):
        content = message.content.lower()
        if any(word in content for word in TRIGGER_WORDS):
            mode = get_mode()
            if mode == "jail":
                # Strip all roles except @everyone, then add jailed role
                jailed_role = message.guild.get_role(JAILED_ROLE_ID)
                if jailed_role:
                    try:
                        roles_to_remove = [role for role in message.author.roles if role.name != "@everyone"]
                        await message.author.remove_roles(*roles_to_remove)
                        await message.author.add_roles(jailed_role)
                    except Exception as e:
                        print(f"Role error: {e}")
            elif mode == "timeout":
                try:
                    await message.author.timeout(discord.utils.utcnow() + discord.timedelta(minutes=10))
                except Exception as e:
                    print(f"Timeout error: {e}")

            try:
                await message.reply("nobody disrespects the owns, faggot")
            except Exception as e:
                print(f"Reply error: {e}")
    await bot.process_commands(message)



@bot.command()
async def togglep(ctx):
    if ctx.author.id not in YOUR_USER_ID:
        return await ctx.send("🚫 You can't use this command.")

    new_mode = toggle_punishment_mode()
    await ctx.send(f"✅ Punishment mode switched to `{new_mode}`.")

@bot.command()
async def akadd(ctx, user_id: str):
    if ctx.author.id not in YOUR_USER_ID:
        return await ctx.send("❌ You are not allowed to use this command.")

    if not user_id.isdigit():
        return await ctx.send("❌ Please provide a valid user ID (numbers only).")

    user_id = int(user_id)
    AUTO_KICK_USERS.add(user_id)
    await ctx.send(f"✅ User ID `{user_id}` added to the auto-kick list.")

@bot.command()
async def akremove(ctx, user_id: str):
    if ctx.author.id not in YOUR_USER_ID:
        return await ctx.send("❌ You are not allowed to use this command.")

    if not user_id.isdigit():
        return await ctx.send("❌ Please provide a valid user ID (numbers only).")

    user_id = int(user_id)
    AUTO_KICK_USERS.discard(user_id)
    await ctx.send(f"🗑️ User ID `{user_id}` removed from the auto-kick list.")


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

@bot.group(invoke_without_command=True)
async def skull(ctx, *, user: discord.User = None):
    if ctx.author.id not in AUTHORIZED_USERS:
        embed = discord.Embed(
            description="🚫 You do not have permission to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if user:
        user_skull_list.add(user.id)
        embed = discord.Embed(
            description=f"💀 Skulling {user.mention} starting now.",
            color=discord.Color.red()
        )
    else:
        embed = discord.Embed(
            title="Help",
            description="Use `.help` or subcommands like `list`, `stop`, `authorize`, etc.",
            color=discord.Color.red()
        )
    await ctx.send(embed=embed)


@skull.command()
async def list(ctx):
    users = [f"<@{uid}>" for uid in user_skull_list]
    embed = discord.Embed(
        title="☠️ Skull List",
        description="\n".join(users) if users else "⚠️ No users being skulled.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


@skull.command()
async def stop(ctx, user: discord.User):
    if user.id in user_skull_list:
        user_skull_list.remove(user.id)
        embed = discord.Embed(
            description=f"✅ {user.mention} will no longer be skulled.",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            description=f"‼️ {user.mention} is not currently being skulled.",
            color=discord.Color.red()
        )
    await ctx.send(embed=embed)


@skull.command()
async def authorized(ctx):
    users = [f"<@{uid}>" for uid in AUTHORIZED_USERS]
    embed = discord.Embed(
        title="✅ Authorized Users",
        description="\n".join(users) if users else "⚠️ No users authorized.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)
    

bot.run(TOKEN)


