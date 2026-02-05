import discord
from discord.ext import commands
import json
import os

DATA_FILE = "economy.json"

# Load economy data
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Save economy data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    def get_balance(self, user_id):
        if str(user_id) not in self.data:
            self.data[str(user_id)] = {"balance": 100}  # default balance
            save_data(self.data)
        return self.data[str(user_id)]["balance"]

    def set_balance(self, user_id, amount):
        self.data[str(user_id)]["balance"] = amount
        save_data(self.data)

    # Balance check command
    @commands.command()
    async def bal(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        bal = self.get_balance(member.id)
        await ctx.send(f"💰 {member.mention} has **{bal} coins**")

    # Add money (admin only)
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addmoney(self, ctx, member: discord.Member, amount: int):
        bal = self.get_balance(member.id)
        new_bal = bal + amount
        self.set_balance(member.id, new_bal)
        await ctx.send(f"✅ Added {amount} coins to {member.mention}. New balance: {new_bal}")

    # Remove money (admin only)
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removemoney(self, ctx, member: discord.Member, amount: int):
        bal = self.get_balance(member.id)
        new_bal = max(0, bal - amount)  # no negative balances
        self.set_balance(member.id, new_bal)
        await ctx.send(f"✅ Removed {amount} coins from {member.mention}. New balance: {new_bal}")

async def setup(bot):
    await bot.add_cog(Economy(bot))
