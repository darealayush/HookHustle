import discord
from discord.ext import commands
import os, threading, json
import dashboard  # Flask dashboard
from dotenv import load_dotenv

# -----------------------------
# Load token and settings
# -----------------------------
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

with open("bot_config.json", "r") as f:
    bot_settings = json.load(f)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=bot_settings["prefix"], intents=intents)
bot.remove_command("help")

dashboard.bot_instance = bot  # Link bot to dashboard

# -----------------------------
# On Ready
# -----------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# -----------------------------
# Load Cogs
# -----------------------------
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def setup_hook():
    await load_cogs()

# -----------------------------
# Start Flask dashboard
# -----------------------------
def run_dashboard():
    dashboard.app.run(host="0.0.0.0", port=5000)

# -----------------------------
# Run Everything
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=run_dashboard, daemon=True).start()
    bot.run(token)
