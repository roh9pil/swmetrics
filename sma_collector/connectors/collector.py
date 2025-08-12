from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCollector(ABC):
    """
    Abstract base class for all data collectors.
    """
    @abstractmethod
    def collect(self) -> List[Dict[str, Any]]:
        """
        Collects data from a source and returns it as a list of dictionaries.
        """
        pass
