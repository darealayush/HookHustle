from flask import Flask, redirect, url_for, session, request, render_template
from flask_session import Session
import requests
import os
from datetime import datetime
from discord.ext import commands
import discord
import dashboard  # to avoid circular import issues


app = Flask(__name__)
app.secret_key = "Di3InOhioFRVR"  # change this to something random and private

bot_instance: commands.Bot = None
bot_start_time = datetime.now()


# ✅ Use filesystem-based session to avoid cookie size limits
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Discord OAuth2 credentials
CLIENT_ID = "1426854615659450478"
CLIENT_SECRET = "fX0oneRbcnum5OCkOMhdKuxYaIAVLo40"
REDIRECT_URI = "http://127.0.0.1:5000/callback"
DISCORD_API_URL = "https://discord.com/api"

# ---------- HOME PAGE ----------
@app.route("/")
def home():
    if "user" in session:
        # Show dashboard if logged in
        user = session["user"]
        return render_template("dashboard.html", user=user)
    else:
        # Otherwise, go to login
        return redirect(url_for("login"))

# ---------- LOGIN ROUTE ----------
@app.route("/login")
def login():
    return redirect(
        f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code&scope=identify"
    )

# ---------- CALLBACK ROUTE ----------
@app.route("/callback")
def callback():
    code = request.args.get("code")

    # Exchange code for an access token
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{DISCORD_API_URL}/oauth2/token", data=data, headers=headers)
    response.raise_for_status()
    access_token = response.json()["access_token"]

    # Get user info from Discord
    user_response = requests.get(
        f"{DISCORD_API_URL}/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_response.raise_for_status()
    user = user_response.json()

    # ✅ Only store the essential data in session
    session["user"] = {
        "id": user["id"],
        "username": user["username"],
        "avatar": user["avatar"]
    }

    return redirect(url_for("home"))

# ---------- LOGOUT ROUTE ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------- RUN SERVER ----------
if __name__ == "__main__":
    app.run(debug=True)



#  ---------- BOT STATS ROUTE ----------
@app.route("/stats")
def stats():
    if "user" not in session:
        return redirect(url_for("login"))

    if not bot_instance:
        return "Bot not connected"

    bot = bot_instance
    uptime = datetime.now() - bot_start_time

    # Calculate total members
    total_members = sum(g.member_count for g in bot.guilds)

    return render_template(
        "stats.html",
        bot_name=bot.user.name,
        bot_avatar=bot.user.display_avatar.url,
        guild_count=len(bot.guilds),
        total_members=total_members,
        ping=round(bot.latency * 1000),
        uptime=str(uptime).split(".")[0]
    )


#---------- BOT SETTINGS ROUTE ----------
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user" not in session:
        return redirect(url_for("login"))

    import json
    import dashboard

    # Load current config safely
    try:
        with open("bot_config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        # If file doesn’t exist, create default
        config = {
            "prefix": "?",
            "modules": {
                "leveling": True,
                "economy": True,
                "moderation": True,
                "fun": True
            }
        }
        with open("bot_config.json", "w") as f:
            json.dump(config, f, indent=4)

    if request.method == "POST":
        # Update prefix safely
        new_prefix = request.form.get("prefix")
        if new_prefix:
            config["prefix"] = new_prefix
            # Update bot prefix if bot instance exists
            if getattr(dashboard, "bot_instance", None):
                dashboard.bot_instance.command_prefix = new_prefix

        # Update module toggles
        for module in config["modules"]:
            # Checkbox returns "on" if checked, None if unchecked
            config["modules"][module] = request.form.get(module) == "on"

        # Save config back to file
        try:
            with open("bot_config.json", "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            return f"Error saving config: {e}", 500

        return redirect(url_for("settings"))

    return render_template("settings.html", config=config)

