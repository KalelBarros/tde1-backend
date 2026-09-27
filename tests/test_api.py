"""
Testes automatizados da API, utilizando pytest e o cliente de testes do Flask.

Para executar:
    pytest -v

Cada teste utiliza um banco de dados SQLite em memória isolado, criado e
populado (com um usuário admin e um usuário autor) pela fixture `client`.
"""

import pytest

from app import create_app
from config import Config
from models import db
from models.usuario import Usuario, TipoUsuario


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "chave-secreta-para-testes"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        admin = Usuario(email="admin@email.com", nome="Administrador", tipo=TipoUsuario.ADMIN)
        admin.definir_senha("admin123")

        autor = Usuario(email="joao@email.com", nome="João Silva", tipo=TipoUsuario.AUTOR)
        autor.definir_senha("autor123")

        db.session.add_all([admin, autor])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def token_admin(client):
    resposta = client.post("/login", json={"email": "admin@email.com", "senha": "admin123"})
    return resposta.get_json()["token"]


def token_autor(client):
    resposta = client.post("/login", json={"email": "joao@email.com", "senha": "autor123"})
    return resposta.get_json()["token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ------------------------------- Login ---------------------------------

def test_login_sucesso_gera_token(client):
    resposta = client.post("/login", json={"email": "admin@email.com", "senha": "admin123"})
    corpo = resposta.get_json()

    assert resposta.status_code == 200
    assert "token" in corpo
    assert isinstance(corpo["token"], str) and len(corpo["token"]) > 0


def test_login_senha_incorreta(client):
    resposta = client.post("/login", json={"email": "admin@email.com", "senha": "senhaerrada"})
    assert resposta.status_code == 401


def test_login_usuario_inexistente(client):
    resposta = client.post("/login", json={"email": "naoexiste@email.com", "senha": "123456"})
    assert resposta.status_code == 401


def test_login_dados_faltando(client):
    resposta = client.post("/login", json={"email": "admin@email.com"})
    assert resposta.status_code == 400


# ------------------------- Acesso sem/ com JWT inválido -----------------

def test_acesso_sem_token(client):
    resposta = client.get("/usuarios")
    assert resposta.status_code == 401


def test_acesso_token_invalido(client):
    resposta = client.get("/usuarios", headers=auth_headers("token-invalido"))
    assert resposta.status_code == 401


def test_acesso_formato_token_invalido(client):
    resposta = client.get("/usuarios", headers={"Authorization": "SemBearer abc"})
    assert resposta.status_code == 401


# ---------------------------- Criar usuário ------------------------------

def test_criar_usuario_como_admin_sucesso(client):
    token = token_admin(client)
    resposta = client.post(
        "/usuarios",
        json={"email": "novo@email.com", "nome": "Novo Usuário", "tipo": "autor", "senha": "123456"},
        headers=auth_headers(token),
    )
    corpo = resposta.get_json()

    assert resposta.status_code == 201
    assert corpo["usuario"]["email"] == "novo@email.com"
    assert corpo["usuario"]["tipo"] == "autor"
    assert "senha" not in corpo["usuario"]
    assert "senha_hash" not in corpo["usuario"]


def test_criar_usuario_sem_permissao_admin(client):
    token = token_autor(client)
    resposta = client.post(
        "/usuarios",
        json={"email": "novo@email.com", "nome": "Novo Usuário", "tipo": "autor", "senha": "123456"},
        headers=auth_headers(token),
    )
    assert resposta.status_code == 403


def test_criar_usuario_email_duplicado(client):
    token = token_admin(client)
    resposta = client.post(
        "/usuarios",
        json={"email": "joao@email.com", "nome": "Outro João", "tipo": "autor", "senha": "123456"},
        headers=auth_headers(token),
    )
    assert resposta.status_code == 409


def test_criar_usuario_tipo_invalido(client):
    token = token_admin(client)
    resposta = client.post(
        "/usuarios",
        json={"email": "x@email.com", "nome": "X", "tipo": "gerente", "senha": "123456"},
        headers=auth_headers(token),
    )
    assert resposta.status_code == 400


def test_criar_usuario_dados_faltando(client):
    token = token_admin(client)
    resposta = client.post("/usuarios", json={"email": "", "nome": "", "tipo": "", "senha": ""},
                            headers=auth_headers(token))
    assert resposta.status_code == 400


# ---------------------------- Listar usuários -----------------------------

def test_listar_usuarios_como_admin(client):
    token = token_admin(client)
    resposta = client.get("/usuarios", headers=auth_headers(token))
    corpo = resposta.get_json()

    assert resposta.status_code == 200
    assert len(corpo["usuarios"]) == 2
    for usuario in corpo["usuarios"]:
        assert "senha" not in usuario
        assert "senha_hash" not in usuario


def test_listar_usuarios_sem_permissao_admin(client):
    token = token_autor(client)
    resposta = client.get("/usuarios", headers=auth_headers(token))
    assert resposta.status_code == 403


# --------------------------- Atualizar usuário ---------------------------

def test_atualizar_proprio_usuario_sucesso(client):
    token = token_autor(client)
    resposta = client.put(
        "/usuarios/2",
        json={"nome": "João Atualizado"},
        headers=auth_headers(token),
    )
    corpo = resposta.get_json()

    assert resposta.status_code == 200
    assert corpo["usuario"]["nome"] == "João Atualizado"


def test_atualizar_usuario_de_outro_sem_permissao(client):
    token = token_autor(client)
    resposta = client.put(
        "/usuarios/1",
        json={"nome": "Tentando alterar admin"},
        headers=auth_headers(token),
    )
    assert resposta.status_code == 403


def test_alterar_senha_com_senha_atual_correta(client):
    token = token_autor(client)
    resposta = client.put(
        "/usuarios/2",
        json={"senha_atual": "autor123", "senha_nova": "novaSenha123"},
        headers=auth_headers(token),
    )
    assert resposta.status_code == 200

    login_antigo = client.post("/login", json={"email": "joao@email.com", "senha": "autor123"})
    assert login_antigo.status_code == 401

    login_novo = client.post("/login", json={"email": "joao@email.com", "senha": "novaSenha123"})
    assert login_novo.status_code == 200


def test_alterar_senha_com_senha_atual_incorreta(client):
    token = token_autor(client)
    resposta = client.put(
        "/usuarios/2",
        json={"senha_atual": "senhaerrada", "senha_nova": "novaSenha123"},
        headers=auth_headers(token),
    )
    assert resposta.status_code == 401


def test_alterar_senha_sem_informar_senha_atual(client):
    token = token_autor(client)
    resposta = client.put(
        "/usuarios/2",
        json={"senha_nova": "novaSenha123"},
        headers=auth_headers(token),
    )
    assert resposta.status_code == 400


# --------------------------- Remover usuário -----------------------------

def test_remover_usuario_como_admin_sucesso(client):
    token = token_admin(client)
    resposta = client.delete("/usuarios/2", headers=auth_headers(token))
    assert resposta.status_code == 200


def test_remover_usuario_sem_permissao_admin(client):
    token = token_autor(client)
    resposta = client.delete("/usuarios/1", headers=auth_headers(token))
    assert resposta.status_code == 403


def test_remover_usuario_inexistente(client):
    token = token_admin(client)
    resposta = client.delete("/usuarios/999", headers=auth_headers(token))
    assert resposta.status_code == 404


def test_remover_usuario_sem_token(client):
    resposta = client.delete("/usuarios/2")
    assert resposta.status_code == 401
