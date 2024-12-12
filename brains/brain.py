from abc import ABC, abstractmethod

class Brain:

    @abstractmethod
    def add_system_prompt(self, system_prompt: str) -> None:
        pass

    @abstractmethod
    def response(self, message: str) -> str:
        pass

    @abstractmethod
    def reset_history(self) -> None:
        pass