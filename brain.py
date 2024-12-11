from mistralai import Mistral

class Brain:
    def __init__(self, api_key: str):
        # Mistral setup
        self.model = "mistral-large-latest"
        self.mistral_client = Mistral(api_key=api_key)

        self.conversation_history = []
    

    def add_system_prompt(self, system_prompt: str):
        self.conversation_history.append({
            "role": "user",
            "content": system_prompt
        })

        
    def response(self, message):
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


    def _add_user_message(self, message):
        self.conversation_history.append({
            "role": "user",
            "content": message
        })