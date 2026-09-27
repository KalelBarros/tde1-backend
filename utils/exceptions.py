"""
Exceções customizadas de negócio.

Centraliza os erros da aplicação em classes com um `status_code` HTTP
associado, permitindo que os Services apenas "lancem" o erro semântico
correto (ex: UsuarioNaoEncontrado) e um único errorhandler no app.py
converta isso em uma resposta JSON padronizada.
"""


class ErroApi(Exception):
    """Classe base para todos os erros de negócio da aplicação."""
    status_code = 400

    def __init__(self, mensagem: str, status_code: int = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        if status_code is not None:
            self.status_code = status_code


class ErroValidacao(ErroApi):
    """Dados inválidos ou incompletos enviados pelo cliente (HTTP 400)."""
    status_code = 400


class NaoAutenticado(ErroApi):
    """Token ausente, inválido ou expirado (HTTP 401)."""
    status_code = 401


class SemPermissao(ErroApi):
    """Usuário autenticado, mas sem permissão para a ação (HTTP 403)."""
    status_code = 403


class UsuarioNaoEncontrado(ErroApi):
    """Usuário não encontrado no banco de dados (HTTP 404)."""
    status_code = 404


class ConflitoDados(ErroApi):
    """Conflito de dados, como email já cadastrado (HTTP 409)."""
    status_code = 409
