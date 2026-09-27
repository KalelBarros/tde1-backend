"""
Script para popular o banco de dados com usuários de exemplo, utilizando
o próprio SQLAlchemy/Werkzeug da aplicação (garante hashes compatíveis
com o mecanismo de login).

Uso:
    python seed.py

Pode ser executado quantas vezes for necessário: usuários cujo email já
exista no banco não serão duplicados.
"""

from app import create_app
from models import db
from models.usuario import Usuario, TipoUsuario

USUARIOS_EXEMPLO = [
    {"email": "admin@email.com", "nome": "Administrador do Sistema", "tipo": TipoUsuario.ADMIN, "senha": "admin123"},
    {"email": "joao@email.com", "nome": "João Silva", "tipo": TipoUsuario.AUTOR, "senha": "autor123"},
    {"email": "maria@email.com", "nome": "Maria Oliveira", "tipo": TipoUsuario.AUTOR, "senha": "autor456"},
]


def popular_banco():
    app = create_app()

    with app.app_context():
        db.create_all()

        for dados in USUARIOS_EXEMPLO:
            existente = Usuario.query.filter_by(email=dados["email"]).first()
            if existente:
                print(f"[SKIP] Usuário já existe: {dados['email']}")
                continue

            usuario = Usuario(email=dados["email"], nome=dados["nome"], tipo=dados["tipo"])
            usuario.definir_senha(dados["senha"])
            db.session.add(usuario)
            print(f"[OK] Usuário criado: {dados['email']} ({dados['tipo']})")

        db.session.commit()
        print("\nBanco de dados populado com sucesso.")


if __name__ == "__main__":
    popular_banco()
