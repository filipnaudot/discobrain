import os
import argparse
import importlib
import yaml

from dotenv import load_dotenv

from backend.preset import PRESETS
from backend.tools import Tools
from backend.characters.base import Character
from backend.brains.brain import Brain
from frontend.discord_handler import DiscordHandler

def class_loader(class_path: str, *args, **kwargs) -> Brain:
    try:
        module_name, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)(*args, **kwargs)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Failed to load brain class '{class_path}': {e}")

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main(brain_path: str, character_path: str, delay: bool) -> None:
    tools = Tools()
    brain: Brain = class_loader(brain_path, tools=tools)
    character: Character = class_loader(character_path)
    brain.add_system_prompt(character.system_prompt())

    discord_handler: DiscordHandler = DiscordHandler(brain, character, delay)
    discord_handler.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.yaml')
    args = parser.parse_args()

    config = load_config(args.config)
    character_key = config.get('character')

    if character_key not in PRESETS:
        raise ValueError(f"Unknown character: {character_key}")

    selected = PRESETS[character_key]
    try:
        main(selected['brain'],
             selected['character'],
             config.get('delay', False))
    except ValueError as e:
        print(e)
