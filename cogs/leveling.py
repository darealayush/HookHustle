import discord
from discord.ext import commands
import random
from utils.storage import load_json, save_json

LEVELS_FILE = "levels.json"

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Load levels from file
        self.levels = load_json(LEVELS_FILE, {})
        self.cooldowns = {}  # prevent spam farming

    def save(self):
        save_json(LEVELS_FILE, self.levels)

    def get_user_data(self, guild_id: int, user_id: int):
        guild_id, user_id = str(guild_id), str(user_id)
        if guild_id not in self.levels:
            self.levels[guild_id] = {}
        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0}
            self.save()
        return self.levels[guild_id][user_id]

    def required_xp(self, level: int) -> int:
        return 100 * (level + 1)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        guild_id, user_id = str(message.guild.id), str(message.author.id)

        # Check cooldown (5 seconds per XP gain)
        key = (guild_id, user_id)
        if key in self.cooldowns and (discord.utils.utcnow() - self.cooldowns[key]).total_seconds() < 5:
            return

        self.cooldowns[key] = discord.utils.utcnow()

        user_data = self.get_user_data(guild_id, user_id)

        # Random XP between 5 and 15
        xp_gain = random.randint(5, 15)
        user_data["xp"] += xp_gain

        # Check for level up
        needed = self.required_xp(user_data["level"])
        if user_data["xp"] >= needed:
            user_data["level"] += 1
            user_data["xp"] -= needed
            self.save()
            await message.channel.send(
                f"🎉 {message.author.mention} leveled up to **Level {user_data['level']}**!"
            )
        else:
            self.save()

    @commands.command(name="level")
    async def level(self, ctx, member: discord.Member = None):
        """Check your level and XP progress."""
        member = member or ctx.author
        data = self.get_user_data(ctx.guild.id, member.id)
        needed = self.required_xp(data["level"])
        await ctx.send(
            f"⭐ {member.mention} is **Level {data['level']}** with `{data['xp']}/{needed}` XP."
        )

    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx):
        """Show the top 5 users by level in this server."""
        guild_id = str(ctx.guild.id)
        guild_data = self.levels.get(guild_id, {})
        if not guild_data:
            return await ctx.send("No data yet!")

        # Sort by level first, then XP
        sorted_users = sorted(
            guild_data.items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )[:5]

        desc = ""
        for i, (user_id, data) in enumerate(sorted_users, start=1):
            user = ctx.guild.get_member(int(user_id)) or f"User {user_id}"
            desc += f"**{i}. {user}** → Level {data['level']} ({data['xp']} XP)\n"

        embed = discord.Embed(
            title=f"🏆 {ctx.guild.name} Leaderboard",
            description=desc,
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
