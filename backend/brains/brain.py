from abc import ABC, abstractmethod
import discord


class Brain:

    @abstractmethod
    def add_system_prompt(self, system_prompt: str) -> None:
        pass

    @abstractmethod
    def response(self, message: discord.Message) -> str:
        pass

    @abstractmethod
    def reset_history(self) -> None:
        pass

    @abstractmethod
    def save_history(self, title: str) -> None:
        pass