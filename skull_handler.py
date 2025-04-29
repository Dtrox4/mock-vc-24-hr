import discord
from discord.ext import commands

# Authorized Users
AUTHORIZED_USERS = {
    1212229549459374222,
    845578292778238002,
    1177672910102614127,
    1305007578857869403,
    1147059630846005318
}

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
                description=f"💀 Skulling {user.mention} starting now.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Skull Help",
                description="Use `.skull help` to view available commands.",
                color=discord.Color.red()
            )
        await ctx.send(embed=embed)

    @skull.command()
    async def authorized(self, ctx):
        users = [f"<@{uid}>" for uid in AUTHORIZED_USERS]
        embed = discord.Embed(
            title="✅ Authorized Users",
            description="\n".join(users) if users else "⚠️ No users authorized.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @skull.command()
    async def list(self, ctx):
        users = [f"<@{uid}>" for uid in user_skull_list]
        embed = discord.Embed(
            title="☠️ Skull List",
            description="\n".join(users) if users else "⚠️ No users being skulled.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @skull.command()
    async def authorize(self, ctx, user: discord.User):
        if user.id not in AUTHORIZED_USERS:
            AUTHORIZED_USERS.add(user.id)
            embed = discord.Embed(
                description=f"✅ {user.mention} has been authorized.",
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
                description="❌ You cannot unauthorize yourself.",
                color=discord.Color.red()
            )
        elif user.id in AUTHORIZED_USERS:
            AUTHORIZED_USERS.remove(user.id)
            embed = discord.Embed(
                description=f"✅ {user.mention} has been unauthorized.",
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
                description=f"✅ {user.mention} will no longer be skulled.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                description=f"‼️ {user.mention} is not currently being skulled.",
                color=discord.Color.red()
            )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.author.id in user_skull_list:
            await message.channel.send(f"💀 {message.author.mention}, you've been skulled.")
        
        await self.bot.process_commands(message)

# Load function
async def setup(bot):
    await bot.add_cog(SkullHandler(bot))
