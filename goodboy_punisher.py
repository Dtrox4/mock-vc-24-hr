# goodboy_punisher.py

import discord
from datetime import timedelta
import re

TRIGGER_KEYWORDS = re.compile(r"\b(good\s?boy|gboy|goodboy)\b", re.IGNORECASE)
TARGET_USER_IDS = {1212229549459374222, 845578292778238002}
WHITELIST_USER_IDS = {1305007578857869403, 1212229549459374222, 845578292778238002}
JAIL_ROLE_ID = 1359325650380652654

# Can be toggled at runtime if needed
PUNISHMENT_MODE = {"mode": "jail"}  # or "timeout"

def toggle_punishment_mode():
    PUNISHMENT_MODE["mode"] = "timeout" if PUNISHMENT_MODE["mode"] == "jail" else "jail"
    return PUNISHMENT_MODE["mode"]

def toggle_punishment_mode():
    global punishment_mode
    punishment_mode = "timeout" if punishment_mode == "jail" else "jail"
    return punishment_mode

async def handle_punishment(message):
    if not message.reference or not message.reference.resolved:
        return

    replied_to = message.reference.resolved.author
    if replied_to.id not in TARGET_USER_IDS:
        return

    if message.author.id in WHITELIST_USER_IDS:
        return  # Ignore whitelisted users

    if not TRIGGER_KEYWORDS.search(message.content):
        return  # No trigger found

    try:
        guild = message.guild
        member = message.author

        if PUNISHMENT_MODE == "timeout":
            await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=10), reason="Disrespect")
        elif PUNISHMENT_MODE == "jail":
            jailed_role = guild.get_role(JAIL_ROLE_ID)
            if jailed_role is None:
                await message.channel.send("⚠️ Jailed role not found.")
                return

            # Remove all roles except @everyone and add jailed role
            roles_to_remove = [role for role in member.roles if role != guild.default_role]
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason="Used banned phrase")

            await member.add_roles(jailed_role, reason="Punishment")

        await message.reply("Nobody disrespects the owns, faggot.")

    except discord.Forbidden:
        await message.channel.send("⚠️ I lack permissions to punish that user.")