"""
Camada de persistência (Models).

Expõe a instância única do SQLAlchemy (db), inicializada em app.py e
utilizada por todos os models da aplicação.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
