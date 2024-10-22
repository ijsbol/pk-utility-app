# PK Utilities App

A helpful utility Discord app to let you see who is fronting in a system.
It can be used in DMs, group chats & servers (including those without PluralKit installed)!

## Ready-to-go app

Add to your account: https://discord.com/oauth2/authorize?client_id=807694126589804614&scope=applications.commands&integration_type=1

Add to your server: https://discord.com/oauth2/authorize?client_id=807694126589804614&scope=applications.commands


## Selfhost guide
1. Install Python3.12+
2. Rename `.env.sample` to `.env`
3. Replace the `DISCORD_BOT_TOKEN` value from `...` to your Discord bot token.
4. Run the following: `python -m pip install venv`
5. Run the following: `python -m venv venv`
6. Run the following: `source venv/bin/activate`
7. Run the following: `pip install -r requirements.txt`
8. Run the following: `cd src`
9. Run the following: `python bot.py`
