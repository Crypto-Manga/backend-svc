from abc import ABC, abstractmethod
from typing import Dict


class BaseHandler(ABC):
    @abstractmethod
    def handle(self, data: Dict):
        pass
