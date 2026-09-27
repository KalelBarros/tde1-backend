"""
Ponto de entrada da aplicação (TDE1 - Backend).

API REST de autenticação e gestão de usuários (admin/autor), construída
em Python + Flask, seguindo o padrão MVC com separação em:
Models, Controllers, Services, Routes, Utils e Config.
"""

import os

from flask import Flask, jsonify

from config import Config
from models import db
from utils.exceptions import ErroApi
from routes.auth_routes import auth_bp
from routes.usuario_routes import usuario_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(usuario_bp)

    @app.route("/")
    def index():
        return jsonify({
            "mensagem": "API TDE1 - Autenticação e gestão de usuários",
            "endpoints": {
                "login": "POST /login (público)",
                "criar_usuario": "POST /usuarios (requer token de admin)",
                "listar_usuarios": "GET /usuarios (requer token de admin)",
                "atualizar_usuario": "PUT /usuarios/<id> (requer token do próprio usuário)",
                "remover_usuario": "DELETE /usuarios/<id> (requer token de admin)",
            },
        }), 200

    # ------------------------- Tratamento de erros -------------------------

    @app.errorhandler(ErroApi)
    def tratar_erro_api(erro: ErroApi):
        """Converte qualquer exceção de negócio (Services) em resposta JSON."""
        return jsonify({"erro": erro.mensagem}), erro.status_code

    @app.errorhandler(400)
    def erro_400(e):
        return jsonify({"erro": "Requisição inválida"}), 400

    @app.errorhandler(404)
    def erro_404(e):
        return jsonify({"erro": "Recurso não encontrado"}), 404

    @app.errorhandler(405)
    def erro_405(e):
        return jsonify({"erro": "Método HTTP não permitido para esta rota"}), 405

    @app.errorhandler(500)
    def erro_500(e):
        db.session.rollback()
        return jsonify({"erro": "Erro interno do servidor"}), 500

    # Cria as tabelas automaticamente caso ainda não existam
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta, debug=app.config["DEBUG"])
