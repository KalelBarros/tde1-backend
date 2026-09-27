"""
Rotas de usuários.

Todas as rotas abaixo exigem um token JWT válido (decorator
`token_required`). As regras de permissão específicas de cada ação
(admin/autor, "somente o próprio usuário", etc.) são aplicadas na
camada de Service, não aqui.
"""

from flask import Blueprint

from controllers.usuario_controller import UsuarioController
from utils.jwt_utils import token_required

usuario_bp = Blueprint("usuarios", __name__)


@usuario_bp.route("/usuarios", methods=["POST"])
@token_required
def criar_usuario():
    return UsuarioController.criar()


@usuario_bp.route("/usuarios", methods=["GET"])
@token_required
def listar_usuarios():
    return UsuarioController.listar()


@usuario_bp.route("/usuarios/<int:usuario_id>", methods=["PUT"])
@token_required
def atualizar_usuario(usuario_id):
    return UsuarioController.atualizar(usuario_id)


@usuario_bp.route("/usuarios/<int:usuario_id>", methods=["DELETE"])
@token_required
def remover_usuario(usuario_id):
    return UsuarioController.remover(usuario_id)
