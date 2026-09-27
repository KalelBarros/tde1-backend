"""
Rotas de autenticação.

POST /login é a única rota pública da aplicação (não exige JWT).
"""

from flask import Blueprint, request, jsonify

from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json(silent=True)
    token = AuthService.login(dados)
    return jsonify({"token": token}), 200
