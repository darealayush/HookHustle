import discord
from discord.ext import commands
from utils.storage import load_json, save_json  # ✅ Import storage helpers

CONFIG_FILE = "config.json"

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Load configs from JSON
        self.configs = load_json(CONFIG_FILE, {})  

    def save(self):
        """Save configs to JSON file."""
        save_json(CONFIG_FILE, self.configs)

    def get_guild_config(self, guild_id: int):
        guild_id = str(guild_id)
        if guild_id not in self.configs:
            self.configs[guild_id] = {"react_channels": [], "modlog_channel": None}
            self.save()
        return self.configs[guild_id]

    @commands.command(name="setreactchannel")
    @commands.has_permissions(manage_guild=True)
    async def set_react_channel(self, ctx, channel: discord.TextChannel):
        """Set a channel where the bot will auto-react to messages."""
        cfg = self.get_guild_config(ctx.guild.id)
        if channel.id not in cfg["react_channels"]:
            cfg["react_channels"].append(channel.id)
            self.save()
        await ctx.send(f"✅ Added {channel.mention} as an auto-react channel.")

    @commands.command(name="removereactchannel")
    @commands.has_permissions(manage_guild=True)
    async def remove_react_channel(self, ctx, channel: discord.TextChannel):
        """Remove a channel from auto-react list."""
        cfg = self.get_guild_config(ctx.guild.id)
        if channel.id in cfg["react_channels"]:
            cfg["react_channels"].remove(channel.id)
            self.save()
            await ctx.send(f"❌ Removed {channel.mention} from auto-react channels.")
        else:
            await ctx.send(f"⚠️ {channel.mention} is not in the list.")

    @commands.command(name="setmodlog")
    @commands.has_permissions(manage_guild=True)
    async def set_modlog(self, ctx, channel: discord.TextChannel):
        """Set the moderation log channel."""
        cfg = self.get_guild_config(ctx.guild.id)
        cfg["modlog_channel"] = channel.id
        self.save()
        await ctx.send(f"📜 Mod-log channel set to {channel.mention}.")

async def setup(bot):
    await bot.add_cog(Config(bot))
