# goodboy_punisher.py

import discord
from datetime import timedelta

JAILED_ROLE_NAME = "jailed"
TARGET_USER_IDS = {
    1212229549459374222,
    845578292778238002,
    1177672910102614127,
}
WHITELIST = {
    1269821629614264362
}

# Default mode
punishment_mode = "jail"  # or "timeout"


def toggle_punishment_mode():
    global punishment_mode
    punishment_mode = "timeout" if punishment_mode == "jail" else "jail"
    return punishment_mode


async def handle_goodboy_trigger(message: discord.Message):
    if message.reference and message.reference.resolved:
        replied_to = message.reference.resolved.author
        if replied_to.id in TARGET_USER_IDS and "good boy" in message.content.lower():
            if message.author.id in WHITELIST:
                return

            guild = message.guild

            if punishment_mode == "jail":
                jailed_role = discord.utils.get(guild.roles, name=JAILED_ROLE_NAME)
                if not jailed_role:
                    jailed_role = await guild.create_role(name=JAILED_ROLE_NAME)
                    for channel in guild.channels:
                        await channel.set_permissions(jailed_role, send_messages=False, speak=False)

                roles_to_remove = [r for r in message.author.roles if r.name != "@everyone"]
                try:
                    await message.author.remove_roles(*roles_to_remove, reason="Used forbidden phrase.")
                    await message.author.add_roles(jailed_role, reason="Punishment: said 'good boy'")
                except discord.Forbidden:
                    print(f"Missing permissions to punish {message.author}")
            else:  # timeout mode
                try:
                    await message.author.timeout(duration=timedelta(minutes=10), reason="Punishment: said 'good boy'")
                except discord.Forbidden:
                    print(f"Missing permissions to timeout {message.author}")

            await message.reply("nobody disrespects the owns, faggot")