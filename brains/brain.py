from abc import ABC, abstractmethod

from tools import Tools


class Brain:

    @abstractmethod
    def add_system_prompt(self, system_prompt: str, tools: Tools) -> None:
        pass

    @abstractmethod
    def response(self, message: str) -> str:
        pass

    @abstractmethod
    def reset_history(self) -> None:
        pass