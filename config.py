"""
Configuração central da aplicação.

Todas as informações sensíveis (chave secreta do JWT, string de conexão
do banco, etc.) são carregadas de variáveis de ambiente, através de um
arquivo .env na raiz do projeto (veja .env.example).

NUNCA coloque valores sensíveis de produção diretamente neste arquivo.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Configurações gerais da aplicação Flask (padrão MVC: Configuração)."""

    # Chave usada para assinar/validar os tokens JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "chave-padrao-apenas-para-desenvolvimento")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_MINUTES = int(os.environ.get("JWT_EXPIRATION_MINUTES", 60))
    JWT_EXPIRATION_DELTA = timedelta(minutes=JWT_EXPIRATION_MINUTES)

    # String de conexão do banco de dados (relacional). Por padrão, SQLite local.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"
