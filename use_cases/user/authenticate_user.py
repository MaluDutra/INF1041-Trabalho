"""Login com e-mail e senha (SCRUM-11)."""

from domain.entities.user import User
from domain.exceptions import InvalidCredentialsError
from use_cases.dtos import AuthenticateUserInput, UserDTO
from use_cases.ports.password_hasher import PasswordHasher
from use_cases.ports.user_repository import UserRepository

INVALID_CREDENTIALS_MESSAGE = "E-mail ou senha incorretos."


class AuthenticateUser:
    """Confere e-mail e senha e devolve o usuário.

    Lança ``InvalidCredentialsError`` com a mesma mensagem para e-mail
    inexistente e para senha errada, sem revelar qual dos dois falhou.
    """

    def __init__(
        self, user_repository: UserRepository, password_hasher: PasswordHasher
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    def execute(self, data: AuthenticateUserInput) -> UserDTO:
        user = self._user_repository.get_by_email(
            User.normalize_email(data.email)
        )
        if user is None or not self._password_hasher.verify(
            data.password, user.password_hash
        ):
            raise InvalidCredentialsError(INVALID_CREDENTIALS_MESSAGE)
        return UserDTO(id=user.id, display_name=user.display_name)
