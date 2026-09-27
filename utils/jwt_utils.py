"""
Utilitários de autenticação JWT (camada de Autenticação).

Contém:
- gerar_token(usuario): cria um token JWT assinado para o usuário.
- decodificar_token(token): decodifica e valida um token JWT.
- token_required: decorator que protege rotas exigindo um token válido
  no header `Authorization: Bearer <token>`.
"""

from functools import wraps
from datetime import datetime, timezone

import jwt
from flask import request, current_app

from models import db
from models.usuario import Usuario
from utils.exceptions import NaoAutenticado


def gerar_token(usuario: Usuario) -> str:
    """Gera um token JWT contendo o id e o tipo do usuário autenticado."""
    payload = {
        "usuario_id": usuario.id,
        "tipo": usuario.tipo,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + current_app.config["JWT_EXPIRATION_DELTA"],
    }
    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decodificar_token(token: str) -> dict:
    """Decodifica e valida um token JWT, levantando NaoAutenticado se inválido/expirado."""
    try:
        return jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
    except jwt.ExpiredSignatureError:
        raise NaoAutenticado("Token expirado")
    except jwt.InvalidTokenError:
        raise NaoAutenticado("Token inválido")


def token_required(f):
    """
    Decorator que exige um token JWT válido no header:
        Authorization: Bearer <token>

    Se válido, injeta o usuário autenticado em `request.usuario_atual`.
    Caso contrário, levanta NaoAutenticado (convertida em HTTP 401 pelo
    errorhandler global da aplicação).
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header:
            raise NaoAutenticado("Token de autenticação não informado")

        partes = auth_header.split()
        if len(partes) != 2 or partes[0] != "Bearer":
            raise NaoAutenticado("Formato do token inválido. Utilize: Bearer <token>")

        payload = decodificar_token(partes[1])

        usuario_atual = db.session.get(Usuario, payload.get("usuario_id"))
        if usuario_atual is None:
            raise NaoAutenticado("Usuário do token não encontrado")

        request.usuario_atual = usuario_atual
        return f(*args, **kwargs)

    return decorated
