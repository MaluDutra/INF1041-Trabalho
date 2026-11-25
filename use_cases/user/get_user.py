"""Consulta de um usuário pelo id, usada para o usuário da sessão."""

from domain.exceptions import NotFoundError
from use_cases.dtos import UserDTO
from use_cases.ports.user_repository import UserRepository


class GetUser:
    """Devolve os dados públicos do usuário ou lança ``NotFoundError``."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def execute(self, user_id: int) -> UserDTO:
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuário não encontrado.")
        return UserDTO(id=user.id, display_name=user.display_name)
