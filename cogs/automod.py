import discord
from discord.ext import commands

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banned_words = ["nigga", "nigger", "nga","niger","niga","bitch","b1tch","b!tch","b!tch","asshole","assh0le","assh1le","assh!le","asshole","assh0le","assh1le","assh!le","retard","r3tard","r3t@rd",]
        self.delete_messages = True

    async def send_modlog(self, guild: discord.Guild, embed: discord.Embed):
        cfg_cog = self.bot.get_cog("Config")
        if not cfg_cog:
            return
        cfg = cfg_cog.get_guild_config(guild.id)
        if cfg["modlog_channel"]:
            channel = guild.get_channel(cfg["modlog_channel"])
            if channel:
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        content_lower = message.content.lower()
        for word in self.banned_words:
            if word in content_lower:
                try:
                    if self.delete_messages:
                        await message.delete()
                        warning = f"🚫 {message.author.mention}, that word isn’t allowed."
                        await message.channel.send(warning, delete_after=5)

                        embed = discord.Embed(
                            title="AutoMod Triggered",
                            description=f"Message by {message.author.mention} deleted.",
                            color=discord.Color.red()
                        )
                        embed.add_field(name="Content", value=message.content, inline=False)
                        await self.send_modlog(message.guild, embed)
                except discord.Forbidden:
                    pass
                break

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
