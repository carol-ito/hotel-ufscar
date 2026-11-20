-- Hotel UFSCar - Sistema de Gestao de Hospedagem
-- schema.sql - PostgreSQL 16
-- Executar uma vez em banco vazio: psql -f schema.sql

CREATE EXTENSION IF NOT EXISTS btree_gist;   -- necessario para a restricao de exclusao

-- ---------------------------------------------------------------
-- Acesso
-- ---------------------------------------------------------------
CREATE TABLE usuario (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome        VARCHAR(120) NOT NULL,
    email       VARCHAR(160) NOT NULL,
    senha_hash  VARCHAR(255) NOT NULL,
    perfil      VARCHAR(10)  NOT NULL CHECK (perfil IN ('GESTAO', 'RECEPCAO')),
    ativo       BOOLEAN      NOT NULL DEFAULT TRUE,
    criado_em   TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX ux_usuario_email ON usuario (lower(email));

-- ---------------------------------------------------------------
-- Hospedes
-- ---------------------------------------------------------------
CREATE TABLE hospede (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome              VARCHAR(120) NOT NULL,
    documento_tipo    VARCHAR(12)  NOT NULL
                      CHECK (documento_tipo IN ('CPF', 'RG', 'PASSAPORTE', 'OUTRO')),
    documento_numero  VARCHAR(30)  NOT NULL,
    email             VARCHAR(160),
    telefone          VARCHAR(20),
    criado_em         TIMESTAMPTZ  NOT NULL DEFAULT now(),
    atualizado_em     TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT ux_hospede_documento UNIQUE (documento_tipo, documento_numero),
    CONSTRAINT ck_hospede_contato   CHECK (email IS NOT NULL OR telefone IS NOT NULL)
);
CREATE INDEX ix_hospede_nome ON hospede (lower(nome) text_pattern_ops);

-- ---------------------------------------------------------------
-- Acomodacoes
-- ---------------------------------------------------------------
CREATE TABLE categoria_acomodacao (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome       VARCHAR(60)  NOT NULL UNIQUE,
    descricao  VARCHAR(255)
);

CREATE TABLE caracteristica (
    id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome  VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE acomodacao (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    numero         VARCHAR(10)   NOT NULL UNIQUE,
    categoria_id   BIGINT        NOT NULL REFERENCES categoria_acomodacao (id),
    capacidade     SMALLINT      NOT NULL CHECK (capacidade > 0),
    valor_diaria   NUMERIC(10,2) NOT NULL CHECK (valor_diaria > 0),
    status         VARCHAR(10)   NOT NULL DEFAULT 'LIVRE'
                   CHECK (status IN ('LIVRE', 'RESERVADO', 'OCUPADO')),
    ativo          BOOLEAN       NOT NULL DEFAULT TRUE,
    criado_em      TIMESTAMPTZ   NOT NULL DEFAULT now(),
    atualizado_em  TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE acomodacao_caracteristica (
    acomodacao_id    BIGINT NOT NULL REFERENCES acomodacao (id) ON DELETE CASCADE,
    caracteristica_id BIGINT NOT NULL REFERENCES caracteristica (id),
    PRIMARY KEY (acomodacao_id, caracteristica_id)
);

-- ---------------------------------------------------------------
-- Reservas (regra central: sem sobreposicao de periodos por acomodacao)
-- Periodo semiaberto [data_entrada, data_saida): a saida de um hospede
-- no dia D libera a acomodacao para uma entrada no mesmo dia D.
-- ---------------------------------------------------------------
CREATE TABLE reserva (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    hospede_id           BIGINT        NOT NULL REFERENCES hospede (id),
    acomodacao_id        BIGINT        NOT NULL REFERENCES acomodacao (id),
    data_entrada         DATE          NOT NULL,
    data_saida           DATE          NOT NULL,
    noites               INTEGER GENERATED ALWAYS AS (data_saida - data_entrada) STORED,
    qtd_hospedes         SMALLINT      NOT NULL CHECK (qtd_hospedes > 0),
    status               VARCHAR(12)   NOT NULL DEFAULT 'PENDENTE'
                         CHECK (status IN ('PENDENTE', 'CONFIRMADA', 'EM_ANDAMENTO',
                                           'ENCERRADA', 'CANCELADA')),
    valor_diaria         NUMERIC(10,2) NOT NULL CHECK (valor_diaria > 0),
    valor_total          NUMERIC(12,2) NOT NULL CHECK (valor_total >= 0),
    motivo_cancelamento  VARCHAR(255),
    criada_por           BIGINT        NOT NULL REFERENCES usuario (id),
    criada_em            TIMESTAMPTZ   NOT NULL DEFAULT now(),
    atualizada_em        TIMESTAMPTZ   NOT NULL DEFAULT now(),
    confirmada_em        TIMESTAMPTZ,
    cancelada_em         TIMESTAMPTZ,
    checkin_em           TIMESTAMPTZ,
    checkout_em          TIMESTAMPTZ,

    CONSTRAINT ck_reserva_periodo CHECK (data_saida > data_entrada),
    CONSTRAINT ck_reserva_cancelamento
        CHECK ((status = 'CANCELADA') = (cancelada_em IS NOT NULL)),
    CONSTRAINT ck_reserva_confirmacao
        CHECK (status NOT IN ('CONFIRMADA', 'EM_ANDAMENTO', 'ENCERRADA')
               OR confirmada_em IS NOT NULL),
    CONSTRAINT ck_reserva_checkin
        CHECK (status NOT IN ('EM_ANDAMENTO', 'ENCERRADA') OR checkin_em IS NOT NULL),
    CONSTRAINT ck_reserva_checkout
        CHECK (status <> 'ENCERRADA' OR checkout_em IS NOT NULL),

    -- Anti-overbooking: duas reservas "vivas" da mesma acomodacao nao podem
    -- ter periodos que se sobrepoem. CANCELADA e ENCERRADA nao bloqueiam.
    CONSTRAINT ex_reserva_sem_sobreposicao
        EXCLUDE USING gist (
            acomodacao_id WITH =,
            daterange(data_entrada, data_saida, '[)') WITH &&
        ) WHERE (status IN ('PENDENTE', 'CONFIRMADA', 'EM_ANDAMENTO'))
);

CREATE INDEX ix_reserva_hospede        ON reserva (hospede_id, data_entrada DESC);
CREATE INDEX ix_reserva_status_entrada ON reserva (status, data_entrada);
CREATE INDEX ix_reserva_criada_em      ON reserva (criada_em);
CREATE INDEX ix_reserva_cancelada_em   ON reserva (cancelada_em) WHERE status = 'CANCELADA';

-- ---------------------------------------------------------------
-- Servicos adicionais e conta da hospedagem
-- ---------------------------------------------------------------
CREATE TABLE servico (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome       VARCHAR(80)   NOT NULL UNIQUE,
    descricao  VARCHAR(255),
    preco      NUMERIC(10,2) NOT NULL CHECK (preco >= 0),
    ativo      BOOLEAN       NOT NULL DEFAULT TRUE
);

CREATE TABLE lancamento_servico (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reserva_id      BIGINT        NOT NULL REFERENCES reserva (id),
    servico_id      BIGINT        NOT NULL REFERENCES servico (id),
    quantidade      INTEGER       NOT NULL CHECK (quantidade > 0),
    valor_unitario  NUMERIC(10,2) NOT NULL CHECK (valor_unitario >= 0),
    valor_total     NUMERIC(12,2) GENERATED ALWAYS AS (quantidade * valor_unitario) STORED,
    lancado_em      TIMESTAMPTZ   NOT NULL DEFAULT now(),
    lancado_por     BIGINT        NOT NULL REFERENCES usuario (id)
);
CREATE INDEX ix_lancamento_reserva ON lancamento_servico (reserva_id);

CREATE TABLE pagamento (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reserva_id      BIGINT        NOT NULL REFERENCES reserva (id),
    metodo          VARCHAR(10)   NOT NULL CHECK (metodo IN ('DINHEIRO', 'PIX', 'CARTAO')),
    valor           NUMERIC(12,2) NOT NULL CHECK (valor > 0),
    pago_em         TIMESTAMPTZ   NOT NULL DEFAULT now(),
    observacao      VARCHAR(255),
    registrado_por  BIGINT        NOT NULL REFERENCES usuario (id)
);
CREATE INDEX ix_pagamento_reserva ON pagamento (reserva_id);
CREATE INDEX ix_pagamento_pago_em ON pagamento (pago_em);

-- Saldo da conta de cada reserva (calculado, nunca armazenado)
CREATE VIEW vw_conta_reserva AS
SELECT r.id AS reserva_id,
       CASE WHEN r.status = 'CANCELADA' THEN 0 ELSE r.valor_total END AS total_diarias,
       COALESCE(s.total, 0)                                           AS total_servicos,
       COALESCE(p.total, 0)                                           AS total_pago,
       CASE WHEN r.status = 'CANCELADA' THEN 0 ELSE r.valor_total END
         + COALESCE(s.total, 0) - COALESCE(p.total, 0)                AS saldo
FROM reserva r
LEFT JOIN (SELECT reserva_id, SUM(valor_total) AS total
           FROM lancamento_servico GROUP BY reserva_id) s ON s.reserva_id = r.id
LEFT JOIN (SELECT reserva_id, SUM(valor) AS total
           FROM pagamento GROUP BY reserva_id) p ON p.reserva_id = r.id;
