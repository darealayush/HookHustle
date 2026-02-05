import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_config(self, guild_id: int):
        cfg_cog = self.bot.get_cog("Config")
        if not cfg_cog:
            return None
        return cfg_cog.get_guild_config(guild_id)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        cfg = self.get_config(member.guild.id)
        if not cfg or not cfg.get("welcome_channel"):
            return

        channel = member.guild.get_channel(cfg["welcome_channel"])
        if channel:
            embed = discord.Embed(
                title="👋 Welcome!",
                description=f"Welcome to **{member.guild.name}**, {member.mention}!",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"We now have {len(member.guild.members)} members!")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        cfg = self.get_config(member.guild.id)
        if not cfg or not cfg.get("goodbye_channel"):
            return

        channel = member.guild.get_channel(cfg["goodbye_channel"])
        if channel:
            embed = discord.Embed(
                title="👋 Goodbye!",
                description=f"{member.mention} has left **{member.guild.name}**.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"We now have {len(member.guild.members)} members.")
            await channel.send(embed=embed)

    @commands.command(name="setwelcome")
    @commands.has_permissions(manage_guild=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        """Set the welcome channel."""
        cfg = self.get_config(ctx.guild.id)
        if cfg is not None:
            cfg["welcome_channel"] = channel.id
            await ctx.send(f"✅ Welcome messages will be sent in {channel.mention}")

    @commands.command(name="setgoodbye")
    @commands.has_permissions(manage_guild=True)
    async def set_goodbye_channel(self, ctx, channel: discord.TextChannel):
        """Set the goodbye channel."""
        cfg = self.get_config(ctx.guild.id)
        if cfg is not None:
            cfg["goodbye_channel"] = channel.id
            await ctx.send(f"✅ Goodbye messages will be sent in {channel.mention}")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
