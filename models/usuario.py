"""
Model: Usuario

Representa a tabela `usuarios` do banco de dados relacional.
Cada usuário possui um `tipo`, que pode ser ADMIN ou AUTOR, e concentra
a lógica de geração/verificação de hash de senha (nunca armazenada em
texto puro).
"""

from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash

from models import db


class TipoUsuario:
    """Enumeração simples dos tipos de usuário permitidos."""
    ADMIN = "admin"
    AUTOR = "autor"

    VALORES = (ADMIN, AUTOR)


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    nome = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default=TipoUsuario.AUTOR)
    senha_hash = db.Column(db.String(255), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint(
            f"tipo IN ('{TipoUsuario.ADMIN}', '{TipoUsuario.AUTOR}')",
            name="ck_usuarios_tipo",
        ),
    )

    # ------------------------------------------------------------------
    # Regras de negócio da própria entidade (Orientação a Objetos)
    # ------------------------------------------------------------------

    def definir_senha(self, senha_texto_plano: str) -> None:
        """Gera e armazena o hash seguro da senha informada."""
        self.senha_hash = generate_password_hash(senha_texto_plano)

    def verificar_senha(self, senha_texto_plano: str) -> bool:
        """Verifica se a senha informada corresponde ao hash armazenado."""
        return check_password_hash(self.senha_hash, senha_texto_plano)

    @property
    def is_admin(self) -> bool:
        return self.tipo == TipoUsuario.ADMIN

    def to_dict(self) -> dict:
        """
        Representação segura do usuário para respostas da API.
        NUNCA inclui a senha ou o hash da senha.
        """
        return {
            "id": self.id,
            "email": self.email,
            "nome": self.nome,
            "tipo": self.tipo,
            "data_criacao": self.data_criacao.isoformat(),
        }

    def __repr__(self):
        return f"<Usuario id={self.id} email={self.email} tipo={self.tipo}>"
