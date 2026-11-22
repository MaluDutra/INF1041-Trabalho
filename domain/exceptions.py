"""Hierarquia de exceções do domínio.

As camadas externas traduzem cada especialização em uma resposta própria
(por exemplo, mensagem de formulário, 404 ou 403).
"""


class DomainError(Exception):
    """Erro base de todas as regras de negócio."""


class ValidationError(DomainError):
    """Dado de entrada que viola uma invariante do domínio."""


class NotFoundError(DomainError):
    """Recurso que não existe."""


class ConflictError(DomainError):
    """Operação que conflita com um recurso já existente."""


class InvalidCredentialsError(DomainError):
    """E-mail ou senha incorretos."""


class PermissionDeniedError(DomainError):
    """Ação que o solicitante não tem permissão de executar."""
