import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

from brains.mistral_api_brain import MistralAPIBrain as Brain
from characters.einstein import Einstein


# Env variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

# Discord intents
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True
intents.typing = False
bot = commands.Bot(command_prefix="!", intents=intents)

brain = Brain(MISTRAL_API_KEY)
character = Einstein()
brain.add_system_prompt(character.system_prompt())



@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord.")

    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print(f"Guild with ID {GUILD_ID} not found.")
        return

    print(f"Connected to guild: {guild.name} (ID: {guild.id})")


@bot.command(name='clear', help='Clears the specified number of messages. Usage: !clear [number]')
async def clear(ctx, amount: int):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("You do not have permission to manage messages.")
        return

    try:
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message
        brain.reset_history()
        await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=1)
    except discord.Forbidden:
        await ctx.send("I don't have permission to delete messages in this channel.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred: {e}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)
    if message.content.startswith("!"): return

    async with message.channel.typing():
        brain_response = brain.response(message.content)

    print(f"\n{character.name()}: {brain_response}\n")
    await message.channel.send(brain_response)


if __name__ == "__main__":
    bot.run(TOKEN)