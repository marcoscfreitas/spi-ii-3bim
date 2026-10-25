CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_servidor_nome_trgm
    ON servidor USING gist (nome gist_trgm_ops);

CREATE INDEX idx_cargo_descricao_trgm
    ON cargo USING gin (descricao gin_trgm_ops);

CREATE INDEX idx_orgao_nome_trgm
    ON orgao USING gin (nome gin_trgm_ops);

CREATE INDEX idx_servidor_cargo_id
    ON servidor (cargo_id);

CREATE INDEX idx_servidor_orgao_id
    ON servidor (orgao_id);

CREATE INDEX idx_servidor_uf_sigla
    ON servidor (uf_sigla);
