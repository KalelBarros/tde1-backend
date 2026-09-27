-- =====================================================================
-- database.sql
-- Projeto: TDE1 - API de Autenticação e Gestão de Usuários
-- Banco: SQLite (relacional)
-- =====================================================================
-- Execução manual (opcional):
--   sqlite3 database.db < database.sql
--
-- OBS: a aplicação (app.py) já cria as tabelas automaticamente na
-- primeira execução via SQLAlchemy (db.create_all()). Este script é
-- entregue para fins acadêmicos/documentação e para permitir a criação
-- e o povoamento manual do banco, conforme exigido pelo enunciado.
-- Use também o script seed.py para popular o banco via ORM.
-- =====================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS usuarios;

-- ---------------------------------------------------------------------
-- Tabela: usuarios
-- ---------------------------------------------------------------------
CREATE TABLE usuarios (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    email          VARCHAR(120)  NOT NULL UNIQUE,
    nome           VARCHAR(120)  NOT NULL,
    tipo           VARCHAR(20)   NOT NULL DEFAULT 'autor',
    senha_hash     VARCHAR(255)  NOT NULL,
    data_criacao   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_usuarios_tipo CHECK (tipo IN ('admin', 'autor'))
);

-- Índice auxiliar para buscas rápidas por email (login)
CREATE UNIQUE INDEX idx_usuarios_email ON usuarios (email);

-- ---------------------------------------------------------------------
-- Dados de exemplo
-- As senhas abaixo NÃO estão em texto puro: são hashes gerados com
-- werkzeug.security.generate_password_hash (mesmo mecanismo usado pela
-- aplicação). As senhas em texto puro, apenas para testes/apresentação,
-- estão indicadas nos comentários.
-- ---------------------------------------------------------------------

-- Usuário ADMIN | senha em texto puro: admin123
INSERT INTO usuarios (email, nome, tipo, senha_hash, data_criacao) VALUES (
    'admin@email.com',
    'Administrador do Sistema',
    'admin',
    'scrypt:32768:8:1$A77DKuLQWhZ7KRc5$5605c5d081c9cd27f5380a21b1eacd95e8ca1820b220916e365838144b2b25d47331fe86686885574c026c8efc5110bb600a8fb0e48f0c89f71e5414e3d1b10b',
    '2024-01-05 08:00:00'
);

-- Usuário AUTOR 1 | senha em texto puro: autor123
INSERT INTO usuarios (email, nome, tipo, senha_hash, data_criacao) VALUES (
    'joao@email.com',
    'João Silva',
    'autor',
    'scrypt:32768:8:1$RtAV05WFr4fPuF7b$35a62cc9d6c7f3a5c48c696e8e16d18e903a0719d71529078b4a0f8d6dd3d1acea47d515a28a4ecbf490177136fe94c3ca8457bd844e7a4ceb228eaff6ab6527',
    '2024-02-10 10:15:00'
);

-- Usuário AUTOR 2 | senha em texto puro: autor456
INSERT INTO usuarios (email, nome, tipo, senha_hash, data_criacao) VALUES (
    'maria@email.com',
    'Maria Oliveira',
    'autor',
    'scrypt:32768:8:1$8H7pae8EGdpr3Kjt$637e9952763732361ae0eb3e005f5ba44688a4161f58b886e7260e03795719f52629d4fbf5cd320f0991afed62b16462b382496a5ba90d08bb440a99cda8511b',
    '2024-03-01 16:40:00'
);
