from abc import ABC, abstractmethod

class Brain:

    @abstractmethod
    def add_system_prompt(self, system_prompt: str):
        pass

    @abstractmethod
    def response(self, message: str):
        pass