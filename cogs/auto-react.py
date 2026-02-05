import discord
from discord.ext import commands

class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reactions = ["👍", "🔥", "😂"]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        cfg_cog = self.bot.get_cog("Config")
        if not cfg_cog:
            return

        cfg = cfg_cog.get_guild_config(message.guild.id)
        if message.channel.id in cfg["react_channels"]:
            for emoji in self.reactions:
                try:
                    await message.add_reaction(emoji)
                except discord.HTTPException:
                    pass

async def setup(bot):
    await bot.add_cog(Reactions(bot))
