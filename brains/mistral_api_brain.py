import json
from mistralai import Mistral
import discord

from .brain import Brain
from tools import Tools

class MistralAPIBrain(Brain):
    def __init__(self, api_key: str, tools: Tools):
        self.model: str = "pixtral-large-latest"
        self.mistral_client = Mistral(api_key=api_key)
        self.tools: Tools = tools
        self.max_tokens: int = 200
        self.system_prompt: str
        self.conversation_history: list = []
    

    def add_system_prompt(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        self.conversation_history.append({
            "role": "user",
            "content": self.system_prompt
        })

        
    def response(self, message: discord.Message) -> str:
        self._add_user_message(message)

        chat_response = self.mistral_client.chat.complete(
            model = self.model,
            tools=self.tools.tool_definitions,
            messages = self.conversation_history,
            max_tokens = self.max_tokens,
            temperature = 0.7,
            safe_prompt = False
        )
        if chat_response.choices[0].message.tool_calls:
            chat_response = self._handle_tool_call(chat_response)

        self._handle_conversation_images()

        self.conversation_history.append({"role": "assistant", "content": chat_response.choices[0].message.content})

        return chat_response.choices[0].message.content
    

    def reset_history(self) -> None:
        self.conversation_history = [{
            "role": "user",
            "content": self.system_prompt
        }]
        

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
                "image_url": image_url
            })
            
        self.conversation_history.append({
            "role": "user",
            "content": message_content
        })


    def _handle_tool_call(self, chat_response):
        self.conversation_history.append(chat_response.choices[0].message)
        tool_call = chat_response.choices[0].message.tool_calls[0]
        function_name = tool_call.function.name
        function_params = json.loads(tool_call.function.arguments)

        print(f"TOOL CALL:\nFunction Name: {function_name}\nParameters: {function_params}")
        # Execute the tool
        function_result = self.tools.names_to_functions[function_name](**function_params)
        print(f"RESULT: {function_result}")

        # Add the tool response to the conversation
        self.conversation_history.append({
            "role": "tool",
            "name": function_name,
            "content": function_result,
            "tool_call_id": tool_call.id
        })

        # Re-call the Mistral API to continue the conversation
        chat_response = self.mistral_client.chat.complete(
            model=self.model,
            tools=self.tools.tool_definitions,
            tool_choice="auto",
            messages=self.conversation_history,
            max_tokens=self.max_tokens,
            temperature=0.7,
            safe_prompt=False
        )

        return chat_response
    

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