"""Relógio real do sistema."""

from datetime import datetime

from use_cases.ports.clock import Clock


class SystemClock(Clock):
    """Hora local, sem fuso: as datas aparecem como o usuário as vive."""

    def now(self) -> datetime:
        return datetime.now()
