import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == CHANNEL_ID:
        role = message.guild.get_role(ROLE_ID)
        if role and role not in message.author.roles:
            await message.author.add_roles(role)
            print(f"{message.author.name} にロール「{role.name}」を付与しました。")

    await bot.process_commands(message)

keep_alive()

if __name__ == "__main__":
    asyncio.run(bot.start(TOKEN))
