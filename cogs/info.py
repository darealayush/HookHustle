import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        embed = discord.Embed(
            title="Hook & Hustle v2.0",
            description="Better Than Ever Before!",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/1376546405040132186/1376546454797287525/A3GDtYDYGsGDAAAAAElFTkSuQmCC.png?ex=68560509&is=6854b389&hm=0a8a272852fe74797f285dd610d73b2c27b79b5785fde1e12e86257e72d47896&=&format=webp&quality=lossless"
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.avatar.url
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def joined(self, ctx, *, member: discord.Member):
        date = member.joined_at.strftime("%B %d, %Y")
        await ctx.send(f"{member} joined on {date}")

    @commands.command()
    async def roles(self, ctx, member: discord.Member):
        roles = [role.name for role in member.roles[1:]]
        await ctx.send("I see the following roles: " + ", ".join(roles))

async def setup(bot):
    await bot.add_cog(Info(bot))
