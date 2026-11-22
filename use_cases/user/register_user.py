"""Cadastro de usuário (SCRUM-11)."""

from domain.entities.user import User
from use_cases.dtos import RegisterUserInput, UserDTO
from use_cases.ports.password_hasher import PasswordHasher
from use_cases.ports.user_repository import UserRepository


class RegisterUser:
    """Valida os dados, gera o hash, grava e devolve o usuário criado.

    Lança ``ValidationError`` para dados inválidos e ``ConflictError``
    se o e-mail já está cadastrado.
    """

    def __init__(
        self, user_repository: UserRepository, password_hasher: PasswordHasher
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    def execute(self, data: RegisterUserInput) -> UserDTO:
        User.validate_password(data.password)
        user = User(
            display_name=data.display_name,
            email=data.email,
            password_hash=self._password_hasher.hash(data.password),
        )
        stored = self._user_repository.add(user)
        return UserDTO(id=stored.id, display_name=stored.display_name)
