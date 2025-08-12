from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCollector(ABC):
    """
    데이터 수집기의 추상 기본 클래스.
    """
    @abstractmethod
    def collect(self) -> List[Dict[str, Any]]:
        pass

