from mistralai import Mistral

from .brain import Brain

class MistralAPIBrain(Brain):
    def __init__(self, api_key: str):
        # Mistral setup
        self.model: str = "mistral-large-latest"
        self.mistral_client = Mistral(api_key=api_key)

        self.system_prompt: str
        self.conversation_history: list = []
    

    def add_system_prompt(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        self.conversation_history.append({
            "role": "user",
            "content": self.system_prompt
        })

        
    def response(self, message: str) -> str:
        self._add_user_message(message)

        chat_response = self.mistral_client.chat.complete(
            model = self.model,
            messages = self.conversation_history,
            max_tokens = 100,
            temperature = 0.7,
            safe_prompt = False
        )
        
        self.conversation_history.append({"role": "assistant", "content": chat_response.choices[0].message.content})
        return chat_response.choices[0].message.content
    

    def reset_history(self) -> None:
        self.conversation_history = [{
            "role": "user",
            "content": self.system_prompt
        }]
        

    def _add_user_message(self, message: str) -> None:
        self.conversation_history.append({
            "role": "user",
            "content": message
        })