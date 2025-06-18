"""Base class for all data fetchers."""

from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    """Abstract interface for all data fetchers."""

    @abstractmethod
    def fetch(self, symbol: str) -> dict:
        """Return data for the provided stock symbol.

        Subclasses should implement this method and return a dictionary
        with provider specific keys and values.
        """
        raise NotImplementedError
