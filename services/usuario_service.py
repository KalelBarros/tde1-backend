"""
Service: UsuarioService

Concentra TODAS as regras de negócio relacionadas ao CRUD de usuários,
incluindo as regras de permissão (quem pode fazer o quê):

- Criar usuário:  somente um usuário ADMIN autenticado.
- Listar usuários: somente um usuário ADMIN autenticado.
- Atualizar usuário: somente o próprio usuário (dono do id).
- Remover usuário: somente um usuário ADMIN autenticado.

Os Controllers apenas chamam estes métodos e traduzem o resultado em
respostas HTTP; a regra de negócio em si vive exclusivamente aqui.
"""

import re

from models import db
from models.usuario import Usuario, TipoUsuario
from utils.exceptions import ErroValidacao, SemPermissao, UsuarioNaoEncontrado, ConflitoDados, NaoAutenticado

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SENHA_TAMANHO_MINIMO = 6


class UsuarioService:

    # ---------------------------------------------------------------
    # Criação
    # ---------------------------------------------------------------
    @staticmethod
    def criar_usuario(dados: dict, usuario_solicitante: Usuario) -> Usuario:
        if not usuario_solicitante.is_admin:
            raise SemPermissao("Somente um usuário administrador pode cadastrar outro usuário")

        if not dados:
            raise ErroValidacao("Corpo da requisição deve ser um JSON válido")

        email = (dados.get("email") or "").strip().lower()
        nome = (dados.get("nome") or "").strip()
        tipo = (dados.get("tipo") or "").strip().lower()
        senha = dados.get("senha") or ""

        if not email or not nome or not tipo or not senha:
            raise ErroValidacao("Os campos 'email', 'nome', 'tipo' e 'senha' são obrigatórios")

        if not EMAIL_REGEX.match(email):
            raise ErroValidacao("Email inválido")

        if tipo not in TipoUsuario.VALORES:
            raise ErroValidacao(f"O campo 'tipo' deve ser um dos seguintes: {', '.join(TipoUsuario.VALORES)}")

        if len(senha) < SENHA_TAMANHO_MINIMO:
            raise ErroValidacao(f"A senha deve ter no mínimo {SENHA_TAMANHO_MINIMO} caracteres")

        if Usuario.query.filter_by(email=email).first() is not None:
            raise ConflitoDados("Já existe um usuário cadastrado com este email")

        novo_usuario = Usuario(email=email, nome=nome, tipo=tipo)
        novo_usuario.definir_senha(senha)

        db.session.add(novo_usuario)
        db.session.commit()

        return novo_usuario

    # ---------------------------------------------------------------
    # Listagem
    # ---------------------------------------------------------------
    @staticmethod
    def listar_usuarios(usuario_solicitante: Usuario) -> list[Usuario]:
        if not usuario_solicitante.is_admin:
            raise SemPermissao("Somente um usuário administrador pode listar os usuários")

        return Usuario.query.order_by(Usuario.id).all()

    # ---------------------------------------------------------------
    # Busca interna (utilizada por outros métodos deste service)
    # ---------------------------------------------------------------
    @staticmethod
    def buscar_usuario_por_id(usuario_id: int) -> Usuario:
        usuario = db.session.get(Usuario, usuario_id)
        if usuario is None:
            raise UsuarioNaoEncontrado("Usuário não encontrado")
        return usuario

    # ---------------------------------------------------------------
    # Atualização
    # ---------------------------------------------------------------
    @staticmethod
    def atualizar_usuario(usuario_id: int, dados: dict, usuario_solicitante: Usuario) -> Usuario:
        if usuario_solicitante.id != usuario_id:
            raise SemPermissao("Você só pode alterar as suas próprias informações")

        usuario = UsuarioService.buscar_usuario_por_id(usuario_id)

        if not dados:
            raise ErroValidacao("Corpo da requisição deve ser um JSON válido")

        nome = dados.get("nome")
        email = dados.get("email")
        senha_atual = dados.get("senha_atual")
        senha_nova = dados.get("senha_nova")

        if nome is not None:
            nome = nome.strip()
            if not nome:
                raise ErroValidacao("O campo 'nome' não pode ser vazio")
            usuario.nome = nome

        if email is not None:
            email = email.strip().lower()
            if not EMAIL_REGEX.match(email):
                raise ErroValidacao("Email inválido")

            email_existente = Usuario.query.filter(
                Usuario.email == email, Usuario.id != usuario_id
            ).first()
            if email_existente is not None:
                raise ConflitoDados("Já existe um usuário cadastrado com este email")

            usuario.email = email

        # Troca de senha exige a senha anterior + a nova senha
        if senha_nova is not None or senha_atual is not None:
            if not senha_atual or not senha_nova:
                raise ErroValidacao(
                    "Para alterar a senha, informe 'senha_atual' e 'senha_nova'"
                )

            if not usuario.verificar_senha(senha_atual):
                raise NaoAutenticado("Senha atual incorreta")

            if len(senha_nova) < SENHA_TAMANHO_MINIMO:
                raise ErroValidacao(f"A nova senha deve ter no mínimo {SENHA_TAMANHO_MINIMO} caracteres")

            usuario.definir_senha(senha_nova)

        db.session.commit()

        return usuario

    # ---------------------------------------------------------------
    # Remoção
    # ---------------------------------------------------------------
    @staticmethod
    def remover_usuario(usuario_id: int, usuario_solicitante: Usuario) -> None:
        if not usuario_solicitante.is_admin:
            raise SemPermissao("Somente um usuário administrador pode remover outro usuário")

        usuario = UsuarioService.buscar_usuario_por_id(usuario_id)

        db.session.delete(usuario)
        db.session.commit()
