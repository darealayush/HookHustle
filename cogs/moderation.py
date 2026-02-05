import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_modlog(self, guild: discord.Guild, embed: discord.Embed):
        cfg_cog = self.bot.get_cog("Config")
        if not cfg_cog:
            return
        cfg = cfg_cog.get_guild_config(guild.id)
        if cfg["modlog_channel"]:
            channel = guild.get_channel(cfg["modlog_channel"])
            if channel:
                await channel.send(embed=embed)

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_member(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member."""
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.mention} has been kicked. Reason: {reason}")

        embed = discord.Embed(
            title="Member Kicked",
            color=discord.Color.orange()
        )
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author}", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        await self.send_modlog(ctx.guild, embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_member(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a member."""
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} has been banned. Reason: {reason}")

        embed = discord.Embed(
            title="Member Banned",
            color=discord.Color.red()
        )
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author}", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        await self.send_modlog(ctx.guild, embed)

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_member(self, ctx, user_id: int):
        """Unban a user by ID."""
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user} has been unbanned.")

        embed = discord.Embed(
            title="Member Unbanned",
            color=discord.Color.green()
        )
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author}", inline=False)
        await self.send_modlog(ctx.guild, embed)

    @commands.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute_member(self, ctx, member: discord.Member, duration: int, *, reason="No reason provided"):
        """Mute a member for X minutes."""
        until = discord.utils.utcnow() + discord.timedelta(minutes=duration)
        await member.timeout(until, reason=reason)
        await ctx.send(f"🔇 {member.mention} has been muted for {duration} minutes. Reason: {reason}")

        embed = discord.Embed(
            title="Member Muted",
            color=discord.Color.dark_gray()
        )
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author}", inline=False)
        embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        await self.send_modlog(ctx.guild, embed)

    @commands.command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    async def unmute_member(self, ctx, member: discord.Member):
        """Unmute a member."""
        await member.timeout(None)  # removes timeout
        await ctx.send(f"🔊 {member.mention} has been unmuted.")

        embed = discord.Embed(
            title="Member Unmuted",
            color=discord.Color.blue()
        )
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author}", inline=False)
        await self.send_modlog(ctx.guild, embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
