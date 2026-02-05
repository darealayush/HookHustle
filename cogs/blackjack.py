import discord
from discord.ext import commands
import random
import json

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Load economy data
    def load_data(self):
        with open("cogs/economy.json", "r", encoding="utf-8") as f:
            return json.load(f)

    # Save economy data
    def save_data(self, data):
        with open("cogs/economy.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # Get or create user data
    def get_user(self, user_id):
        data = self.load_data()
        if str(user_id) not in data:
            data[str(user_id)] = {"wallet": 0, "bank": 0, "inventory": {}}
            self.save_data(data)
        return data

    # Calculate hand value
    def hand_value(self, hand):
        value = 0
        aces = 0
        for card in hand:
            if card in ["J", "Q", "K"]:
                value += 10
            elif card == "A":
                value += 11
                aces += 1
            else:
                value += int(card)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    # Deal card
    def deal_card(self):
        cards = [str(n) for n in range(2,11)] + ["J","Q","K","A"]
        return random.choice(cards)

    @commands.command()
    async def blackjack(self, ctx, bet: int):
        user_id = str(ctx.author.id)
        data = self.get_user(user_id)
        wallet = data[user_id]["wallet"]

        if bet <= 0:
            return await ctx.send("❌ Bet must be greater than 0!")
        if bet > wallet:
            return await ctx.send("❌ You don't have enough coins!")

        # Initialize hands
        player_hand = [self.deal_card(), self.deal_card()]
        dealer_hand = [self.deal_card(), self.deal_card()]

        def format_hand(hand):
            return " ".join(hand)

        # Check for blackjack immediately
        player_value = self.hand_value(player_hand)
        dealer_value = self.hand_value(dealer_hand)

        if player_value == 21:
            data[user_id]["wallet"] += int(1.5*bet)
            self.save_data(data)
            return await ctx.send(f"🎉 Blackjack! You win {int(1.5*bet)} coins!\nYour hand: {format_hand(player_hand)}\nDealer: {format_hand(dealer_hand)}")

        # Game loop
        player_turn = True
        while player_turn:
            embed = discord.Embed(
                title="🎴 Blackjack",
                description=f"Your hand: {format_hand(player_hand)} (Value: {self.hand_value(player_hand)})\nDealer: {dealer_hand[0]} ?",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Type 'hit' to draw a card, 'stand' to hold.")
            await ctx.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.content.lower() in ["hit","stand"]

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30)
            except:
                return await ctx.send("⌛ Time's up! Game cancelled.")

            if msg.content.lower() == "hit":
                player_hand.append(self.deal_card())
                if self.hand_value(player_hand) > 21:
                    data[user_id]["wallet"] -= bet
                    self.save_data(data)
                    return await ctx.send(f"💥 Bust! You lose {bet} coins.\nYour hand: {format_hand(player_hand)}")
            else:
                player_turn = False

        # Dealer turn
        while self.hand_value(dealer_hand) < 17:
            dealer_hand.append(self.deal_card())

        player_value = self.hand_value(player_hand)
        dealer_value = self.hand_value(dealer_hand)

        if dealer_value > 21 or player_value > dealer_value:
            data[user_id]["wallet"] += bet
            result = f"🎉 You win {bet} coins!"
        elif player_value < dealer_value:
            data[user_id]["wallet"] -= bet
            result = f"💥 You lose {bet} coins!"
        else:
            result = "🤝 Push! No coins won or lost."

        self.save_data(data)
        await ctx.send(f"{result}\nYour hand ({player_value}): {format_hand(player_hand)}\nDealer ({dealer_value}): {format_hand(dealer_hand)}")

# Setup cog
async def setup(bot):
    await bot.add_cog(Blackjack(bot))
