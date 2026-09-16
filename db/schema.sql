CREATE TABLE cargo (
    id BIGINT PRIMARY KEY,
    descricao TEXT NOT NULL
);

CREATE TABLE orgao (
    id BIGINT PRIMARY KEY,
    nome TEXT NOT NULL
);

CREATE TABLE uf (
    sigla VARCHAR(2) PRIMARY KEY
);

CREATE TABLE servidor (
    id BIGINT PRIMARY KEY,
    nome TEXT NOT NULL,
    cargo_id BIGINT NOT NULL REFERENCES cargo (id),
    orgao_id BIGINT NOT NULL REFERENCES orgao (id),
    uf_sigla VARCHAR(2) REFERENCES uf (sigla)
);
