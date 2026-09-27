"""
Service: AuthService

Concentra a regra de negócio da autenticação (login).
"""

from models.usuario import Usuario
from utils.jwt_utils import gerar_token
from utils.exceptions import ErroValidacao, NaoAutenticado


class AuthService:

    @staticmethod
    def login(dados: dict) -> str:
        """
        Autentica um usuário por email e senha.
        Retorna o token JWT gerado em caso de sucesso.
        Levanta ErroValidacao (400) ou NaoAutenticado (401) caso contrário.
        """
        if not dados:
            raise ErroValidacao("Corpo da requisição deve ser um JSON válido")

        email = (dados.get("email") or "").strip().lower()
        senha = dados.get("senha") or ""

        if not email or not senha:
            raise ErroValidacao("Os campos 'email' e 'senha' são obrigatórios")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario is None or not usuario.verificar_senha(senha):
            raise NaoAutenticado("Email ou senha inválidos")

        return gerar_token(usuario)
