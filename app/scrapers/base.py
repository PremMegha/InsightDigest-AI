from abc import ABC, abstractmethod

class BaseScraper(ABC):
    source_name: str

    @abstractmethod
    def fetch_articles(self):
        pass
