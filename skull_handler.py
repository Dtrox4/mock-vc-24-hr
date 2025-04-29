import discord
from discord.ext import commands

# Replace with your Discord User ID
YOUR_USER_ID = 1212229549459374222

# Authorized users
AUTHORIZED_USERS = {YOUR_USER_ID, 845578292778238002, 1177672910102614127, 1305007578857869403, 1147059630846005318}

AUTHORIZED_USERS = set()
user_skull_list = set()

class SkullHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def skull(self, ctx, *, user: discord.User = None):
        if ctx.author.id not in AUTHORIZED_USERS:
            embed = discord.Embed(
                description="You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if user:
            user_skull_list.add(user.id)
            embed = discord.Embed(
                description=f"✅️ Skulling {user.mention} starting now.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Help commands",
                description="⚠️ Use `.skull help (1, 2, 3)` to view command help pages.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @skull.command()
    async def authorized(self, ctx):
        authorized_users = [f'<@{user_id}>' for user_id in AUTHORIZED_USERS]
        embed = discord.Embed(
            title="✅️ Authorized Users",
            description="\n".join(authorized_users) if authorized_users else "⚠️ No users are authorized.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @skull.command()
    async def list(self, ctx):
        skull_users = [f'<@{user_id}>' for user_id in user_skull_list]
        embed = discord.Embed(
            title="☠️ Skull List",
            description="\n".join(skull_users) if skull_users else "⚠️ No users are currently being skulled.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @skull.command()
    async def authorize(self, ctx, user: discord.User):
        if user.id not in AUTHORIZED_USERS:
            AUTHORIZED_USERS.add(user.id)
            embed = discord.Embed(
                description=f"✅️ {user.mention} has been authorized to use the commands.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                description=f"‼️ {user.mention} is already authorized.",
                color=discord.Color.red()
            )
        await ctx.send(embed=embed)

    @skull.command()
    async def unauthorize(self, ctx, user: discord.User):
        if user.id == ctx.author.id:
            embed = discord.Embed(
                description="❌️ You cannot unauthorize yourself.",
                color=discord.Color.red()
            )
        elif user.id in AUTHORIZED_USERS:
            AUTHORIZED_USERS.remove(user.id)
            embed = discord.Embed(
                description=f"✅️ {user.mention} has been unauthorized.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                description=f"‼️ {user.mention} is not in the authorized list.",
                color=discord.Color.red()
            )
        await ctx.send(embed=embed)

    @skull.command()
    async def stop(self, ctx, user: discord.User):
        if user.id in user_skull_list:
            user_skull_list.remove(user.id)
            embed = discord.Embed(
                description=f"✅️ {user.mention} will no longer be skulled.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                description=f"‼️ {user.mention} is not currently being skulled.",
                color=discord.Color.red()
            )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SkullHandler(bot))
