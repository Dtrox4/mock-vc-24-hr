import discord
from discord.ext import commands
import os
import json
from pathlib import Path
from homoglyphs import Homoglyphs
import re
from dotenv import load_dotenv
from datetime import timedelta
from flask import Flask, request, jsonify
import asyncio
from threading import Thread
from punishment_config import get_mode, toggle_punishment_mode
from jail_utils import store_user_roles, retrieve_user_roles
from word_counter import increment_word_count, get_tracked_words, add_word, remove_word, get_word_count

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
TOKEN = os.getenv('DISCORD_TOKEN')

YOUR_USER_ID = {
    1212229549459374222,
    845578292778238002,
    1238152637959110679,
    1088004084084256839
}

AUTHORIZED_USERS = {
    1212229549459374222,
    845578292778238002,
    1177672910102614127,
    1088004084084256839,
    1238152637959110679
}

#BOYS
TRIGGER_KEYWORDS = re.compile(r"\b(good\s?boy|gboy|kys|faggot|goodboy|badboy|bad\s?boy)\b", re.IGNORECASE)
TARGET_USER_IDS = {1212229549459374222, 845578292778238002, 1177672910102614127}
WHITELIST_USER_IDS = {1305007578857869403, 1212229549459374222, 845578292778238002, 1177672910102614127, 1088004084084256839, 1177672910102614127}
JAILED_ROLE_ID = 1359325650380652654

#MARYAM
TRIGGER_M = re.compile(r"\b(good\s?girl|mommy|shawty|bitch|whore|goodgirl|hoe|slut|faggot|badgirl|shawty|baby|babe|bae|pookie)\b", re.IGNORECASE)
TARGET_USER_M = 1269821629614264362
WHITELIST_USER_M = {1305007578857869403, 1212229549459374222, 767662700725403658, 940295461753987132, 713576608136429618, 1369688693337624650, 1003140111258624011, 1196446087972667555, 764189912740134932, 1170371030410350734, 1212398197972926496, 755954707436142593}

h = Homoglyphs()

BANNED_WORDS_PATTERN = re.compile(
    r"""\b(
        r[\W_]*[a@4][\W_]*p[\W_]*[e3]([ds]?)?             # rape variations
        | r[\W_]*[p][\W_]*[e3]                            # more rape variations
        | n[\W_]*[i1!|][\W_]*[gq69][\W_]*[e3][\W_]*[r]+   # nigger variations
    )\b""",
    re.IGNORECASE | re.VERBOSE
)

# Define channels and optional messages
WELCOME_CHANNELS = {
    1359328373356363987: None,
    1369944674495893534: None,
    1366327489122668644: None,
    1359319883988336924: "hey loser! bst & main for roles."  # Add a custom message here
}

AUTO_KICK_USERS = set()

#handle multiple punishment error
handled_messages = set()

# Users being skulled
user_skull_list = set()

# Define the intents
intents=discord.Intents.all()
intents.reactions = True
intents.messages = True
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

    content = message.content.lower()
    for word in get_tracked_words():
        if word in content:
            increment_word_count(word)

    # Only run homoglyph normalization if suspicious characters found
    if any(ord(c) > 127 for c in message.content):  # non-ASCII detected
        normalized = "".join(h.to_ascii(message.content))
    else:
        normalized = message.content
    
    # Now check for banned words (outside the else block)
    if BANNED_WORDS_PATTERN.search(normalized):
        try:
            await message.delete()
            warning = await message.channel.send(
                f"🚫 {message.author.mention}, your message contained a prohibited word and was removed."
            )
            await asyncio.sleep(5)
            await warning.delete()
        except discord.Forbidden:
            print("Missing permissions to delete a message.")
        except Exception as e:
            print(f"Error deleting message: {e}")


    await bot.process_commands(message)

    if message.author.id in user_skull_list:
        try:
            await asyncio.sleep(1)
            await message.add_reaction("☠️")
        except discord.Forbidden:
            print(f"Missing permissions to react in {message.channel.name}")
        except discord.HTTPException as e:
            print(f"Failed to add reaction: {e}")

    if message.id in handled_messages:
        return
    handled_messages.add(message.id)


    if not message.reference or not message.reference.resolved:
        return

    replied_to = message.reference.resolved.author

    if (
        (replied_to.id in TARGET_USER_IDS and TRIGGER_KEYWORDS.search(message.content.lower()) and message.author.id not in WHITELIST_USER_IDS)
        or
        (replied_to.id == TARGET_USER_M and TRIGGER_M.search(message.content.lower()) and message.author.id not in WHITELIST_USER_M)
    ):
        try:
            if get_mode() == "jail":
                jailed_role = message.guild.get_role(JAILED_ROLE_ID)
                if jailed_role:
                    # inside the jail block
                    roles_to_remove = [
                        r for r in message.author.roles
                        if r != message.guild.default_role and r.id != JAILED_ROLE_ID
                    ]
                    store_user_roles(message.author.id, [r.id for r in roles_to_remove])
                    await message.author.add_roles(jailed_role)
                    await message.author.remove_roles(*roles_to_remove)
                    # Send the message in the jail channel
                    jail_channel = bot.get_channel(1359325648912515264)
                    if jail_channel:
                        await jail_channel.send(
                            f"<@{message.author.id}>, you have been jailed. Please wait for a staff member to discuss your jail. "
                            "For more information, your bitchass go jailed cause you can't behave sit down slut."
                        )

                    else:
                        print("⚠️ Jail channel not found.")
                else:
                    print("Jailed role not found.")
            elif get_mode() == "timeout":
                await message.author.timeout(
                    discord.utils.utcnow() + timedelta(minutes=10),
                    reason="Disrespectful message"
                )
        except Exception as e:
            print(f"Punishment error: {e}")

        try:
            if replied_to.id in TARGET_USER_IDS:
                await message.reply("know your place, dumb nigga.", mention_author=True)
            elif replied_to.id == TARGET_USER_M:
                await message.reply("nuh uh you're cooked.", mention_author=True)
        except Exception as e:
            print(f"Reply error: {e}")

@bot.command()
async def togglep(ctx):
    if ctx.author.id not in YOUR_USER_ID:
        return await ctx.send("🚫 You can't use this command.")
    new_mode = toggle_punishment_mode()
    await ctx.send(f"✅ Punishment mode switched to `{new_mode}`.")

@bot.command(name="unjail")
@commands.has_permissions(manage_roles=True)
async def unjail(ctx, member: discord.Member):
    jailed_role = ctx.guild.get_role(JAILED_ROLE_ID)
    if jailed_role and jailed_role in member.roles:
        try:
            await member.remove_roles(jailed_role)
            role_ids = retrieve_user_roles(member.id)
            roles = [ctx.guild.get_role(rid) for rid in role_ids if ctx.guild.get_role(rid)]
            if roles:
                await member.add_roles(*roles)
            await ctx.send(f"{member.mention} has been unjailed and roles restored.")
        except Exception as e:
            await ctx.send(f"Error unjailing: {e}")
    else:
        await ctx.send("User is not jailed.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def jail(ctx, member: discord.Member):
    jailed_role = ctx.guild.get_role(JAILED_ROLE_ID)
    if not jailed_role:
        return await ctx.send("❌ Jailed role not found.")

    roles_to_remove = [r for r in member.roles if r != ctx.guild.default_role and r.id != JAILED_ROLE_ID]
    try:
        await member.remove_roles(*roles_to_remove, reason="Testing jail")
        await member.add_roles(jailed_role, reason="Testing jail")
        store_user_roles(member.id, [r.id for r in roles_to_remove])
        await ctx.send(f"✅ {member.mention} has been jailed successfully.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to modify that user's roles.")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, *args):
    if not args:
        return await ctx.send("⚠️ Please specify at least one word to filter messages by.")

    limit = 200
    keywords = [arg.lower() for arg in args if not arg.isdigit()]
    limit_args = [int(arg) for arg in args if arg.isdigit()]
    if limit_args:
        limit = min(limit_args[0], 200)

    def check(m):
        return any(word in m.content.lower() for word in keywords)

    deleted = await ctx.channel.purge(limit=limit, check=check)
    confirm = await ctx.send(f"🧹 Deleted {len(deleted)} message(s) containing: {', '.join(keywords)}.")
    await asyncio.sleep(5)
    await confirm.delete()

@bot.command()
async def cadd(ctx, word: str):
    if add_word(word):
        await ctx.send(f"✅ Started tracking `{word}`.")
    else:
        await ctx.send(f"⚠️ `{word}` is already being tracked.")

@bot.command()
async def cremove(ctx, word: str):
    if remove_word(word):
        await ctx.send(f"🗑️ Stopped tracking `{word}`.")
    else:
        await ctx.send(f"❌ `{word}` was not being tracked.")

@bot.command()
async def count(ctx, word: str):
    count = get_word_count(word)
    embed = discord.Embed(title="Word Count", color=discord.Color.blurple())
    embed.add_field(name="Word", value=word, inline=True)
    embed.add_field(name="Count", value=f"`{count}`", inline=True)
    await ctx.send(embed=embed)


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


@bot.command(name="authorized")
async def show_authorized(ctx):
    try:
        with open("authorized_users.json", "r") as f:
            authorized_users = json.load(f)
    except FileNotFoundError:
        authorized_users = []

    if not authorized_users:
        embed = discord.Embed(
            title="👮 Authorized Users",
            description="No users are currently authorized.",
            color=discord.Color.red()
        )
    else:
        user_mentions = []
        for user_id in authorized_users:
            user = ctx.guild.get_member(int(user_id))
            user_mentions.append(user.mention if user else f"`{user_id}` (Not in server)")

        embed = discord.Embed(
            title="👮 Authorized Users",
            description="\n".join(user_mentions),
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Total: {len(user_mentions)}")

    await ctx.send(embed=embed)


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


