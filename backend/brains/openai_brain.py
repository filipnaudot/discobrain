import json
import os

from dotenv import load_dotenv
from openai import OpenAI
import discord

from backend.brains.brain import Brain
from backend.tools import Tools

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class OpenAIAPIBrain(Brain):
    def __init__(self, *args, **kwargs):
        self.model: str = "gpt-4o-mini"
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
        self.tools: Tools = kwargs.pop('tools', None)        
        # if self.tools is None: raise ValueError("Missing required 'tools' argument")
        
        self.max_tokens: int = 500
        self.system_prompt: str
        self.conversation_history: list = []
    

    def add_system_prompt(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })

        
    def response(self, message: discord.Message) -> str:
        self._add_user_message(message)

        chat_response = self.client.chat.completions.create(
                model = self.model,
                messages = self.conversation_history,
                max_tokens = self.max_tokens,
            )
        

        self._handle_conversation_images()

        self.conversation_history.append({"role": "assistant", "content": chat_response.choices[0].message.content})

        return chat_response.choices[0].message.content
    

    def reset_history(self) -> None:
        self.conversation_history = [{
            "role": "user",
            "content": self.system_prompt
        }]
    

    def save_history(self, title: str) -> None:
        os.makedirs("./conversations/", exist_ok=True)
        file_path = f"./conversations/{title}.json"
        with open(file_path, "w") as json_file:
            json.dump(self.conversation_history, json_file, indent=4)
        
        
    def _add_user_message(self, message: discord.Message) -> None:
        image_url: str | None = ""
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    image_url = attachment.url
                    print(f"Image URL: {attachment.url}")

        message_content = [{
            "type": "text",
            "text": message.content
        },]
        if image_url:
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url
                },
            })
            
        self.conversation_history.append({
            "role": "user",
            "content": message_content
        })
    

    def _handle_conversation_images(self):
        """
        Handles images in the conversation history.

        This function ensures that only one image at a time is supported in the conversation. If an image is present
        in the last message, it is immediately removed from the history.
        """
        # TODO: Implement a max image check instead that allows a max_images number of images.
        
        if not self.conversation_history:
            return

        last_message = self.conversation_history[-1]
        if "content" in last_message and isinstance(last_message["content"], list):            
            self.conversation_history[-1]["content"] = [item for item in last_message["content"] if item.get("type") != "image_url"]