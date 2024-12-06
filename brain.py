from mistralai import Mistral

class Brain:
    def __init__(self, api_key: str):
        # Mistral setup
        model = "mistral-large-latest"
        mistral_client = Mistral(api_key=api_key)
        