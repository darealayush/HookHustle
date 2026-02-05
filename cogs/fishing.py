import discord
from discord.ext import commands
import json, random, os
from datetime import datetime, timedelta

class Fishing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

        # Fish definitions
        self.fishes = [
            {"name": "🐟 Common Fish", "price": 50, "rarity": "Common", "weight": 60,
             "image": "https://media.discordapp.net/attachments/1376546405040132186/1417854291657621574/image-removebg-preview.png"},
            {"name": "🦑 Squid", "price": 150, "rarity": "Uncommon", "weight": 25,
             "image": "https://media.discordapp.net/attachments/1376546405040132186/1417854692519837816/image-removebg-preview_1.png"},
            {"name": "🐠 Rare Fish", "price": 300, "rarity": "Rare", "weight": 10,
             "image": "https://media.discordapp.net/attachments/1376546405040132186/1417854884132421643/Pixel-Art-Fish-6-removebg-preview.png"},
            {"name": "🐉 Legendary Sea Dragon", "price": 1000, "rarity": "Legendary", "weight": 5,
             "image": "https://media.discordapp.net/attachments/1376546405040132186/1417855558974832660/image-removebg-preview_2.png"}
        ]

        # Fish mutations
        self.mutations = [
            {"name": "Rainbow", "multiplier": 3, "chance": 2},
            {"name": "Golden", "multiplier": 2, "chance": 5},
            {"name": "Shiny", "multiplier": 1.5, "chance": 10},
            {"name": "Mega", "multiplier": 5, "chance": 1}
        ]

        self.file_path = "cogs/economy.json"
        # Ensure JSON exists
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    # Load economy data safely
    def load_data(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}  # return empty dict if file is empty or invalid

    # Save economy data
    def save_data(self, data):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # Get or create user
    def get_user(self, user_id):
        data = self.load_data()
        if str(user_id) not in data:
            data[str(user_id)] = {"wallet": 0, "bank": 0, "inventory": {}}
            self.save_data(data)
        return data

    # Apply mutation to fish
    def apply_mutation(self, fish):
        roll = random.randint(1, 100)
        current = 0
        for m in self.mutations:
            current += m["chance"]
            if roll <= current:
                fish["mutation"] = m["name"]
                fish["price"] = int(fish["price"] * m["multiplier"])
                break
        return fish

    # -----------------------------
    # Commands
    # -----------------------------
    @commands.command()
    async def fish(self, ctx):
        user_id = str(ctx.author.id)
        now = datetime.now()

        # Cooldown check
        if user_id in self.cooldowns:
            expire_time = self.cooldowns[user_id] + timedelta(seconds=5)
            if now < expire_time:
                remaining = (expire_time - now).seconds
                return await ctx.send(f"⏳ You need to wait {remaining}s before fishing again!")

        # Pick fish and apply mutation
        fish = random.choices(self.fishes, weights=[f["weight"] for f in self.fishes])[0].copy()
        fish = self.apply_mutation(fish)

        # Update inventory
        data = self.get_user(user_id)
        user_data = data[user_id]
        inventory = user_data.setdefault("inventory", {})

        fish_key = fish["name"]
        if "mutation" in fish:
            fish_key = f"{fish['mutation']} {fish['name']}"
        inventory[fish_key] = inventory.get(fish_key, 0) + 1

        self.save_data(data)
        self.cooldowns[user_id] = now

        # Embed colors by rarity
        color_dict = {
            "Common": discord.Color.light_grey(),
            "Uncommon": discord.Color.green(),
            "Rare": discord.Color.blue(),
            "Legendary": discord.Color.gold()
        }

        embed_title = f"🎣 You caught a {fish['rarity']} fish!"
        if "mutation" in fish:
            embed_title += f" ✨ {fish['mutation']}!"

        embed = discord.Embed(
            title=embed_title,
            description=f"{fish_key} added to your inventory!",
            color=color_dict.get(fish["rarity"], discord.Color.default())
        )

        if "image" in fish:
            embed.set_thumbnail(url=fish["image"])

        await ctx.send(embed=embed)

    @commands.command(aliases=["inv"])
    async def inventory(self, ctx):
        user_id = str(ctx.author.id)
        data = self.get_user(user_id)
        inventory = data[user_id].get("inventory", {})

        if not inventory:
            return await ctx.send("👜 Your inventory is empty!")

        # Sort inventory by rarity and then name
        sorted_inventory = sorted(inventory.items(), key=lambda x: (
            next((["Common","Uncommon","Rare","Legendary"].index(f["rarity"]) 
                  for f in self.fishes if f["name"] in x[0]), 0), x[0]))

        embed = discord.Embed(title=f"{ctx.author.name}'s Inventory", color=discord.Color.blue())
        for item, amount in sorted_inventory:
            rarity = next((f["rarity"] for f in self.fishes if f["name"] in item), "Common")
            embed.add_field(name=f"{item} ({rarity})", value=f"x{amount}", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def sell(self, ctx, *, fish_name: str):
        user_id = str(ctx.author.id)
        data = self.get_user(user_id)
        user_data = data[user_id]
        inventory = user_data.get("inventory", {})
        fish_name = fish_name.strip()

        # Build price dict
        prices = {f["name"]: f["price"] for f in self.fishes}
        for f in self.fishes:
            for m in self.mutations:
                prices[f"{m['name']} {f['name']}"] = int(f["price"] * m["multiplier"])

        if fish_name not in inventory or inventory[fish_name] <= 0:
            return await ctx.send("❌ You don’t have that fish in your inventory!")

        # Sell fish
        inventory[fish_name] -= 1
        if inventory[fish_name] == 0:
            del inventory[fish_name]

        user_data["wallet"] += prices.get(fish_name, 0)
        self.save_data(data)

        await ctx.send(f"💰 You sold **{fish_name}** for **{prices[fish_name]} coins**!")

    @commands.command()
    async def sellall(self, ctx):
        user_id = str(ctx.author.id)
        data = self.get_user(user_id)
        user_data = data[user_id]
        inventory = user_data.get("inventory", {})

        if not inventory:
            return await ctx.send("👜 Your inventory is empty!")

        prices = {f["name"]: f["price"] for f in self.fishes}
        for f in self.fishes:
            for m in self.mutations:
                prices[f"{m['name']} {f['name']}"] = int(f["price"] * m["multiplier"])

        total_earned, sold_items = 0, []
        for item, amount in list(inventory.items()):
            earned = prices.get(item, 0) * amount
            total_earned += earned
            sold_items.append(f"{item} x{amount} → {earned} coins")
            del inventory[item]

        user_data["wallet"] += total_earned
        self.save_data(data)

        embed = discord.Embed(
            title="💰 Sell All",
            description="\n".join(sold_items),
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Total Earned: {total_earned} coins")
        await ctx.send(embed=embed)

# Setup cog
async def setup(bot):
    await bot.add_cog(Fishing(bot))
