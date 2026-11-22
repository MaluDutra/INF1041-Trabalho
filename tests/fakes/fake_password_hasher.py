"""Fake determinístico do PasswordHasher, reaproveitado pelos testes."""

from use_cases.ports.password_hasher import PasswordHasher


class FakePasswordHasher(PasswordHasher):
    PREFIX = "hashed:"

    def hash(self, password: str) -> str:
        return f"{self.PREFIX}{password[::-1]}"

    def verify(self, password: str, password_hash: str) -> bool:
        return self.hash(password) == password_hash
