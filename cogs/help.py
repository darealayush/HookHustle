import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="# H&H Help Menu ",
            description="Here are all the commands you can use!\nUse `?command` to run them.",
            color=discord.Color.purple()
        )

        # Example categories
        embed.add_field(name="🎲 Gambling", value="`blackjack` - Play Blackjack, ``", inline=False)
        embed.add_field(name="🎣 Fishing", value="`fish`, `inventory`, `sell`, `sellall`", inline=False)
        embed.add_field(name="💰 Economy", value="`bal`, `addmoney`, `removemoney`", inline=False)
        embed.add_field(name="📈 Leveling", value="`level`, `leaderboard`", inline=False)
        embed.add_field(name="🛠 Moderation", value="`ban`, `kick`, `mute`, `unmute`, `unban`", inline=False)
        embed.add_field(name="ℹ️ Info", value="`info`, `joined`, `roles`", inline=False)
        embed.add_field(name="👋 Welcome", value="`setwelcome`, `setgoodbye`", inline=False)
        embed.add_field(name="⚙️ Config", value="`setmodlog`, `setreactchannel`, `removereactchannel`", inline=False)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_author(name="Infinity Bot", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
