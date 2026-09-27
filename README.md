# TDE1 — API de Autenticação e Gestão de Usuários

## 1. Descrição / Objetivo

Este projeto corresponde à **primeira etapa (TDE1)** de um sistema acadêmico de Backend. O foco desta etapa é exclusivamente:

- Autenticação de usuários via **JWT**;
- Gestão de usuários (**criação, atualização, remoção e listagem**), com dois tipos de usuário: **admin** e **autor**, cada um com regras de permissão distintas.

Funcionalidades como cursos, disciplinas, questões, avaliações, templates e geração de PDF **não fazem parte** desta etapa.

## 2. Tecnologias utilizadas

- **Python 3**
- **Flask** — framework web
- **Flask-SQLAlchemy** — ORM / persistência relacional
- **SQLite** — banco de dados relacional
- **PyJWT** — geração e validação de tokens JWT
- **Werkzeug (security)** — hash seguro de senhas (scrypt)
- **python-dotenv** — variáveis de ambiente
- **pytest** — testes automatizados

## 3. Estrutura do projeto (padrão MVC)

```
tde1-backend/
│
├── app.py                     # Ponto de entrada; cria a aplicação Flask (application factory)
├── config.py                  # Configurações carregadas de variáveis de ambiente
├── database.sql               # Script SQL de criação das tabelas + dados de exemplo
├── seed.py                    # Popula o banco com dados de exemplo via ORM
├── requirements.txt           # Dependências do projeto
├── .env.example                # Modelo do arquivo de variáveis de ambiente
├── .gitignore
├── README.md
│
├── models/                    # MODEL — entidades e persistência
│   ├── __init__.py            # Instância do SQLAlchemy (db)
│   └── usuario.py             # Model Usuario (id, email, nome, tipo, senha_hash)
│
├── controllers/                # CONTROLLER — recebe a requisição e delega ao service
│   ├── __init__.py
│   └── usuario_controller.py
│
├── services/                   # Regras de negócio (permissões, validações)
│   ├── __init__.py
│   ├── auth_service.py         # Lógica de login/autenticação
│   └── usuario_service.py      # Lógica de CRUD + permissões de usuários
│
├── routes/                     # Definição dos endpoints (Blueprints)
│   ├── __init__.py
│   ├── auth_routes.py          # POST /login (pública)
│   └── usuario_routes.py       # /usuarios (protegidas por JWT)
│
├── utils/                      # Autenticação e utilidades
│   ├── __init__.py
│   ├── jwt_utils.py            # Geração/validação de JWT + decorator token_required
│   └── exceptions.py           # Exceções de negócio (400/401/403/404/409)
│
└── tests/
    ├── __init__.py
    └── test_api.py             # Testes automatizados (pytest)
```

**Fluxo de uma requisição:** `routes` (recebe a requisição e aplica `token_required`) → `controllers` (extrai dados e chama o service) → `services` (regra de negócio e permissões) → `models` (persistência via SQLAlchemy).

## 4. Como instalar o Python

Baixe e instale o Python 3.10+ em https://www.python.org/downloads/ (marque a opção "Add Python to PATH" no Windows). Para verificar a instalação:

```bash
python3 --version
```

## 5. Como criar o ambiente virtual

Na raiz do projeto:

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\activate
```

## 6. Como instalar as dependências (requirements.txt)

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

## 7. Como configurar o `.env`

Copie o arquivo de exemplo e ajuste os valores:

```bash
# Linux / macOS
cp .env.example .env

# Windows
copy .env.example .env
```

Conteúdo do `.env.example`:

```env
DATABASE_URL=sqlite:///database.db
JWT_SECRET_KEY=troque-esta-chave-por-uma-chave-secreta-forte
JWT_EXPIRATION_MINUTES=60
FLASK_DEBUG=True
PORT=5000
```

> Troque `JWT_SECRET_KEY` por um valor aleatório antes de apresentar/publicar o projeto.

## 8. Como criar e popular o banco de dados

Existem duas formas (escolha uma):

**Opção A — Automática (recomendada):** a própria aplicação cria as tabelas automaticamente ao iniciar (`db.create_all()` em `app.py`). Basta rodar o script de dados de exemplo:

```bash
python seed.py
```

**Opção B — Manual, via script SQL:** utilize o `database.sql` diretamente com o `sqlite3`:

```bash
sqlite3 database.db < database.sql
```

Ambas as opções deixam o banco no mesmo estado: 1 usuário `admin` e 2 usuários `autor`.

## 9. Como executar a API

```bash
python app.py
```

A API sobe em `http://localhost:5000` (porta configurável via `.env`).

## 10. Como fazer login e utilizar o JWT

1. Envie um `POST /login` com `email` e `senha`.
2. Copie o `token` retornado.
3. Envie esse token em todas as demais requisições, no header:

```
Authorization: Bearer SEU_TOKEN_AQUI
```

Se o token estiver ausente, inválido ou expirado, a API responde `401`.

## 11. Usuários de exemplo (dados de teste)

| Email | Senha | Tipo |
|---|---|---|
| admin@email.com | admin123 | admin |
| joao@email.com | autor123 | autor |
| maria@email.com | autor456 | autor |

## 12. Endpoints implementados

| Método | Rota | Autenticação | Regra de permissão |
|---|---|---|---|
| POST | `/login` | Pública | — |
| POST | `/usuarios` | JWT obrigatório | Somente **admin** |
| GET | `/usuarios` | JWT obrigatório | Somente **admin** |
| PUT | `/usuarios/<id>` | JWT obrigatório | Somente o **próprio usuário** |
| DELETE | `/usuarios/<id>` | JWT obrigatório | Somente **admin** |

## 13. Exemplos de requisições e respostas

### POST /login

```json
{
  "email": "admin@email.com",
  "senha": "admin123"
}
```

Resposta `200`:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Resposta `401` (credenciais inválidas):
```json
{ "erro": "Email ou senha inválidos" }
```

### POST /usuarios (requer token de admin)

Header: `Authorization: Bearer <token_admin>`

```json
{
  "email": "usuario@email.com",
  "nome": "João Silva",
  "tipo": "autor",
  "senha": "123456"
}
```

Resposta `201`:
```json
{
  "mensagem": "Usuário criado com sucesso",
  "usuario": {
    "id": 4,
    "email": "usuario@email.com",
    "nome": "João Silva",
    "tipo": "autor",
    "data_criacao": "2026-01-01T10:00:00"
  }
}
```

Resposta `403` (usuário autenticado não é admin):
```json
{ "erro": "Somente um usuário administrador pode cadastrar outro usuário" }
```

Resposta `409` (email duplicado):
```json
{ "erro": "Já existe um usuário cadastrado com este email" }
```

### GET /usuarios (requer token de admin)

Resposta `200`:
```json
{
  "usuarios": [
    { "id": 1, "email": "admin@email.com", "nome": "Administrador do Sistema", "tipo": "admin", "data_criacao": "2024-01-05T08:00:00" },
    { "id": 2, "email": "joao@email.com", "nome": "João Silva", "tipo": "autor", "data_criacao": "2024-02-10T10:15:00" }
  ]
}
```
*(a senha/hash nunca é retornada)*

### PUT /usuarios/\<id\> (requer token do próprio usuário)

Alterar nome/email:
```json
{ "nome": "João da Silva", "email": "joao.silva@email.com" }
```

Alterar senha (exige a senha atual):
```json
{ "senha_atual": "autor123", "senha_nova": "novaSenha456" }
```

Resposta `200`:
```json
{
  "mensagem": "Usuário atualizado com sucesso",
  "usuario": { "id": 2, "email": "joao.silva@email.com", "nome": "João da Silva", "tipo": "autor", "data_criacao": "2024-02-10T10:15:00" }
}
```

Resposta `403` (tentando alterar outro usuário):
```json
{ "erro": "Você só pode alterar as suas próprias informações" }
```

Resposta `401` (senha atual incorreta):
```json
{ "erro": "Senha atual incorreta" }
```

### DELETE /usuarios/\<id\> (requer token de admin)

Resposta `200`:
```json
{ "mensagem": "Usuário removido com sucesso" }
```

Resposta `404`:
```json
{ "erro": "Usuário não encontrado" }
```

## 14. Códigos HTTP utilizados

| Código | Significado |
|---|---|
| 200 | Operação realizada com sucesso |
| 201 | Usuário criado com sucesso |
| 400 | Dados inválidos ou incompletos |
| 401 | Não autenticado / token ausente, inválido ou expirado / senha incorreta |
| 403 | Autenticado, mas sem permissão para a ação |
| 404 | Usuário não encontrado |
| 409 | Conflito — email já cadastrado |
| 500 | Erro interno do servidor |

## 15. Como testar com Postman / Insomnia

1. Crie uma requisição `POST http://localhost:5000/login` com body JSON `{"email": "admin@email.com", "senha": "admin123"}`.
2. Copie o `token` da resposta.
3. Nas demais requisições, vá em **Headers** e adicione: `Authorization: Bearer <token copiado>`.
4. Teste os endpoints da tabela da seção 12, variando o usuário logado (admin x autor) para observar as respostas `403`.
5. Uma coleção pode ser montada manualmente com as 5 requisições (`login`, `criar`, `listar`, `atualizar`, `remover`) usando os exemplos da seção 13.

## 16. Como rodar os testes automatizados

```bash
pytest -v
```

Os testes cobrem: login correto, login com senha incorreta, criação de usuário (admin), criação sem permissão, email duplicado, listagem (admin e sem permissão), atualização do próprio usuário, tentativa de atualizar outro usuário, troca de senha (com senha atual correta/incorreta), remoção (admin e sem permissão), remoção de usuário inexistente, acesso sem token e com token inválido.

Todos os testes utilizam um banco SQLite **em memória**, isolado da base de desenvolvimento (`database.db`).
