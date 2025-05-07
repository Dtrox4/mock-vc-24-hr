# goodboy_punisher.py

import discord
from datetime import timedelta
import re

TRIGGER_KEYWORDS = re.compile(r"\b(good\s?boy|gboy|goodboy)\b", re.IGNORECASE)
TARGET_USER_IDS = {1212229549459374222, 845578292778238002}
WHITELIST_USER_IDS = {1305007578857869403, 1212229549459374222, 845578292778238002}
JAIL_ROLE_ID = 1359325650380652654

# punishment_config.py

PUNISHMENT_MODE = {"mode": "jail"}  # or "timeout"

def get_mode():
    return PUNISHMENT_MODE["mode"]

def toggle_punishment_mode():
    PUNISHMENT_MODE["mode"] = "timeout" if PUNISHMENT_MODE["mode"] == "jail" else "jail"
    return PUNISHMENT_MODE["mode"]

async def handle_punishment(message):
    member = message.author
    guild = message.guild

    jailed_role = guild.get_role(1359325650380652654)
    if not jailed_role:
        await message.reply("❌ Jailed role not found.")
        return

    try:
        if punishment_mode == "jail":
            # Remove all roles except @everyone
            roles_to_remove = [role for role in member.roles if role != guild.default_role]
            await member.remove_roles(*roles_to_remove, reason="Triggered jail punishment")

            # Add jailed role
            await member.add_roles(jailed_role, reason="Jailed for disrespect")
            await message.reply("Nobody disrespects the owns, faggot.")

        elif punishment_mode == "timeout":
            # Timeout for 10 minutes
            duration = 600  # 10 minutes in seconds
            until = discord.utils.utcnow() + datetime.timedelta(seconds=duration)
            await member.timeout(until, reason="Timeout punishment")
            await message.reply("Nobody disrespects the owns, faggot.")

    except discord.Forbidden:
        await message.reply("❌ I don’t have permission to change that user’s roles.")
    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")
