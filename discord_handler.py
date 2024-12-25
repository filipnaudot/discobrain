import os
import argparse
import importlib
from dotenv import load_dotenv

import discord
from discord.ext import commands

from tools import Tools
from characters.base import Character
from brains.brain import Brain

# Env variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))



class DiscordHandler:
    def __init__(self, brain: Brain, character: Character) -> None:
        self.brain: Brain = brain
        self.character: Character = character
        # Discord intents
        self.intents = discord.Intents.default()
        self.intents.members = True
        self.intents.presences = True
        self.intents.message_content = True
        self.intents.typing = False
        self.bot = commands.Bot(command_prefix="!", intents=self.intents)
    
    def run(self) -> None:
        #############
        # COMMANDS  #
        #############
        @self.bot.command(name='clear', help='Clears the specified number of messages. Usage: !clear [number]')
        async def clear(ctx, amount: int):
            if not ctx.author.guild_permissions.manage_messages:
                await ctx.send("You do not have permission to manage messages.")
                return
            try:
                deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message
                self.brain.reset_history()
                await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=1)
            except discord.Forbidden:
                await ctx.send("I don't have permission to delete messages in this channel.")
            except discord.HTTPException as e:
                await ctx.send(f"An error occurred: {e}")
        
        @self.bot.command(name='save', help='Save the conversation history as JSON. Usage: !save [title]')
        async def save_conversation(ctx, title: str):
            if not ctx.author.guild_permissions.manage_messages:
                await ctx.send("You do not have permission to manage messages.")
                return
            try:
                self.brain.save_history(title)
                await ctx.send(f"Conversation saved.", delete_after=1)
            except discord.Forbidden:
                await ctx.send("I don't have permission to delete messages in this channel.")
            except discord.HTTPException as e:
                await ctx.send(f"An error occurred: {e}")
        
        @self.bot.command(name='list', help='Lists all saved conversations. Usage: !list')
        async def list_conversations(ctx):
            folder_path = "./conversations"
            if not os.path.exists(folder_path):
                await ctx.send("The conversations folder does not exist.")
                return
            files = os.listdir(folder_path)
            json_files = [file for file in files if file.endswith(".json")]
            file_list = "\n".join(json_files)
            await ctx.send(f"Saved conversations:\n```\n{file_list}\n```")

        ###########
        # EVENTS  #
        ###########
        @self.bot.event
        async def on_ready():
            print(f"{self.bot.user} has connected to Discord.")
            guild = self.bot.get_guild(GUILD_ID)
            if guild is None:
                print(f"Guild with ID {GUILD_ID} not found.")
                return
            print(f"Connected to guild: {guild.name} (ID: {guild.id})")

        @self.bot.event
        async def on_message(message: discord.Message):
            if message.author == self.bot.user:
                return

            await self.bot.process_commands(message)
            if message.content.startswith("!"): return

            async with message.channel.typing():
                brain_response = self.brain.response(message)

            print(f"\n{self.character.name()}: {brain_response}\n")
            await message.channel.send(brain_response)

        self.bot.run(TOKEN)