"""Relógio fixo, para datas determinísticas nos testes."""

from datetime import datetime

from use_cases.ports.clock import Clock


class FixedClock(Clock):
    def __init__(self, moment: datetime) -> None:
        self.moment = moment

    def now(self) -> datetime:
        return self.moment
