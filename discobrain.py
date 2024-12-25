import os
import argparse
import importlib
from dotenv import load_dotenv

import discord
from discord.ext import commands

from tools import Tools
from characters.base import Character
from brains.brain import Brain
from discord_handler import DiscordHandler

def class_loader(class_path: str, *args, **kwargs) -> Brain:
    try:
        module_name, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        # class_object = getattr(module, class_name)(*args, **kwargs)
        return getattr(module, class_name)(*args, **kwargs) # class_object(*args, **kwargs)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Failed to load brain class '{class_path}': {e}")


def main(brain_path: str, character_path: str) -> None:
    tools = Tools()
    brain: Brain = class_loader(brain_path, tools=tools)
    character: Character = class_loader(character_path)
    brain.add_system_prompt(character.system_prompt())

    discord_handler: DiscordHandler = DiscordHandler(brain, character)
    discord_handler.run()


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
