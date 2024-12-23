import os
import argparse
import importlib
from dotenv import load_dotenv

import discord
from discord.ext import commands

from tools import Tools
from characters.base import Character
from brains.brain import Brain


def load_character(class_path: str) -> Character:
    try:
        module_name, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        character_class = getattr(module, class_name)
        return character_class()
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Failed to load character class '{class_path}': {e}")

def load_brain(class_path: str, *args, **kwargs) -> Brain:
    try:
        module_name, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        brain_class = getattr(module, class_name)
        return brain_class(*args, **kwargs)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Failed to load brain class '{class_path}': {e}")


def main(brain_path: str, character_path: str) -> None:
    # Env variables
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))
    API_KEY = os.getenv('API_KEY')

    # Discord intents
    intents = discord.Intents.default()
    intents.members = True
    intents.presences = True
    intents.message_content = True
    intents.typing = False
    bot = commands.Bot(command_prefix="!", intents=intents)

    tools = Tools()
    brain: Brain = load_brain(brain_path, api_key=API_KEY, tools=tools)
    character: Character = load_character(character_path)
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
    async def on_message(message: discord.Message):
        if message.author == bot.user:
            return

        await bot.process_commands(message)
        if message.content.startswith("!"): return

        async with message.channel.typing():
            brain_response = brain.response(message)

        print(f"\n{character.name()}: {brain_response}\n")
        await message.channel.send(brain_response)

    bot.run(TOKEN)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DiscoBrain Discord Bot")
    parser.add_argument(
        "--character",
        type=str,
        required=True,
        help="Specify the character to use in the format 'module.submodule.ClassName'. For example: 'characters.einstein.Einstein'."
    )
    parser.add_argument(
        "--brain",
        type=str,
        required=True,
        help="Specify the brain to use in the format 'module.submodule.ClassName'. For example: 'brains.mistral_api_brain.MistralAPIBrain'."
    )
    args = parser.parse_args()

    try:
        main(args.brain, args.character)
    except ValueError as e:
        print(e)
