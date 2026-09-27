"""
Controller: UsuarioController

Camada responsável por receber a requisição HTTP (via Flask `request`),
repassar os dados para o Service correto e traduzir o resultado (ou a
exceção de negócio levantada) em uma resposta HTTP/JSON.

Nenhuma regra de negócio deve existir aqui — apenas orquestração entre
a rota e o service.
"""

from flask import jsonify, request

from services.usuario_service import UsuarioService


class UsuarioController:

    @staticmethod
    def criar():
        dados = request.get_json(silent=True)
        usuario = UsuarioService.criar_usuario(dados, request.usuario_atual)
        return jsonify({
            "mensagem": "Usuário criado com sucesso",
            "usuario": usuario.to_dict(),
        }), 201

    @staticmethod
    def listar():
        usuarios = UsuarioService.listar_usuarios(request.usuario_atual)
        return jsonify({
            "usuarios": [usuario.to_dict() for usuario in usuarios]
        }), 200

    @staticmethod
    def atualizar(usuario_id: int):
        dados = request.get_json(silent=True)
        usuario = UsuarioService.atualizar_usuario(usuario_id, dados, request.usuario_atual)
        return jsonify({
            "mensagem": "Usuário atualizado com sucesso",
            "usuario": usuario.to_dict(),
        }), 200

    @staticmethod
    def remover(usuario_id: int):
        UsuarioService.remover_usuario(usuario_id, request.usuario_atual)
        return jsonify({"mensagem": "Usuário removido com sucesso"}), 200
