import gc
import json
import os

from dotenv import load_dotenv
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    Pipeline,
    pipeline,
)
import torch
import discord

from .brain import Brain
from tools import Tools

load_dotenv()
HF_TOKEN: str = os.getenv('HUGGINGFACE_TOKEN')
MODEL_NAME: str = os.getenv('HUGGINGFACE_MODEL_NAME')


class HuggingfaceModelLoader(Brain):
    def __init__(self, tools: Tools):
        # TODO: Unpack kwargs indstead of params
        self.model_name: str = MODEL_NAME
        self.quantize: bool = True
        self.tokenizer:AutoTokenizer = AutoTokenizer.from_pretrained(self.model_name, token=HF_TOKEN)
        self.device:str = "cuda" if torch.cuda.is_available() else "cpu"

        self.max_tokens: int = 200
        self.system_prompt: str
        self.conversation_history: list = []

        if self.quantize:
            self.model = self._load_quantized_model()
        else:
            self.model = self.model_name

        self.generator: Pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            pad_token_id=self.tokenizer.eos_token_id,
            token=HF_TOKEN,
        )


    def add_system_prompt(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        self.conversation_history.append({
            "role": "user",
            "content": self.system_prompt
        })

    
    def response(self, message: discord.Message) -> str:
        self._add_user_message(message)
        chat_response = self.generator(
            self.conversation_history,
            do_sample=True,
            temperature=0.7,
            top_p=0.6,
            max_new_tokens=self.max_tokens,
        )

        self.conversation_history.append({"role": "assistant", "content": chat_response[0]['generated_text'][-1]['content']})

        return chat_response[0]['generated_text'][-1]['content']
    

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

    
    def cleanup(self):        
        del self.generator
        self.generator = None
        del self.tokenizer
        self.tokenizer = None
        del self.model
        self.model = None
        gc.collect()

        torch.cuda.empty_cache()
    

    def _add_user_message(self, message: discord.Message) -> None:     
        self.conversation_history.append({
            "role": "user",
            "content": message.content
        })


    def _load_quantized_model(self):
        print("Loading quantized model...")
        bnb_config = BitsAndBytesConfig(load_in_4bit=True)

        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            token=HF_TOKEN,
        )

        return model