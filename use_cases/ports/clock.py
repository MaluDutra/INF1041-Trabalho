"""Port do relógio (permite datas determinísticas nos testes)."""

from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime:
        """Devolve o instante atual."""
