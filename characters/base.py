from abc import ABC, abstractmethod

class Character(ABC):
    @abstractmethod
    def name(self) -> str:
        """Return the name of the character."""
        pass

    @abstractmethod
    def description(self) -> str:
        """Return a description of the character."""
        pass

    @abstractmethod
    def personality(self) -> str:
        """Return the personality traits of the character."""
        pass

    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for the character."""
        pass