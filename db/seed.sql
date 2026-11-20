-- Hotel UFSCar - dados FICTICIOS para desenvolvimento e homologacao (LGPD: nenhum dado real).
-- Executar depois do schema.sql, uma vez, em banco vazio. O Docker Compose faz isso sozinho no primeiro start.
-- Logins de teste (senha de todos: senha123):  gestao@hotel.local  |  recepcao@hotel.local
-- TROQUE as senhas se este banco for exposto na internet.

INSERT INTO usuario (nome, email, senha_hash, perfil) VALUES
  ('Gestora Teste',  'gestao@hotel.local',   '$2b$12$8OwcxBunG8m3slY05O1lTu9yVIIacXj9DQMN.hxUk8T/.JLcQl/H.', 'GESTAO'),
  ('Recepção Teste', 'recepcao@hotel.local', '$2b$12$8OwcxBunG8m3slY05O1lTu9yVIIacXj9DQMN.hxUk8T/.JLcQl/H.', 'RECEPCAO');

INSERT INTO categoria_acomodacao (nome, descricao) VALUES
  ('Standard', 'Quarto simples com banheiro privativo'),
  ('Luxo', 'Quarto amplo com varanda'),
  ('Suíte Família', 'Suíte com duas camas de casal');

INSERT INTO caracteristica (nome) VALUES
  ('Ar-condicionado'), ('Frigobar'), ('TV'), ('Varanda'), ('Wi-Fi'), ('Banheira');

INSERT INTO acomodacao (numero, categoria_id, capacidade, valor_diaria) VALUES
  ('101', 1, 2, 150.00), ('102', 1, 2, 150.00), ('103', 1, 3, 180.00), ('104', 1, 3, 180.00),
  ('201', 2, 2, 260.00), ('202', 2, 2, 260.00), ('203', 2, 3, 300.00), ('204', 2, 3, 300.00),
  ('301', 3, 4, 420.00), ('302', 3, 4, 420.00), ('303', 3, 5, 480.00), ('304', 3, 6, 540.00);

-- toda acomodação tem Wi-Fi e TV; as demais variam por categoria
INSERT INTO acomodacao_caracteristica (acomodacao_id, caracteristica_id)
  SELECT a.id, c.id FROM acomodacao a, caracteristica c WHERE c.nome IN ('Wi-Fi', 'TV');
INSERT INTO acomodacao_caracteristica (acomodacao_id, caracteristica_id)
  SELECT a.id, c.id FROM acomodacao a, caracteristica c WHERE a.categoria_id >= 2 AND c.nome IN ('Ar-condicionado', 'Frigobar');
INSERT INTO acomodacao_caracteristica (acomodacao_id, caracteristica_id)
  SELECT a.id, c.id FROM acomodacao a, caracteristica c WHERE a.categoria_id = 2 AND c.nome = 'Varanda';
INSERT INTO acomodacao_caracteristica (acomodacao_id, caracteristica_id)
  SELECT a.id, c.id FROM acomodacao a, caracteristica c WHERE a.categoria_id = 3 AND c.nome = 'Banheira';

INSERT INTO hospede (nome, documento_tipo, documento_numero, email, telefone) VALUES
  ('Maria Souza',     'CPF', '12345678909', 'maria.souza@exemplo.com',  '16999990001'),
  ('João Pereira',    'CPF', '98765432100', 'joao.pereira@exemplo.com', NULL),
  ('Ana Lima',        'CPF', '11144477735', NULL,                       '16999990003'),
  ('Carlos Mendes',   'CPF', '24681357928', 'carlos@exemplo.com',       '16999990004'),
  ('Beatriz Rocha',   'CPF', '13579246828', 'beatriz@exemplo.com',      NULL),
  ('John Smith',      'PASSAPORTE', 'XK1234567', 'john.smith@exemplo.com', NULL);

-- Reservas de exemplo, sempre relativas a hoje. Inseridas direto no banco (a API não aceita entrada no passado).
WITH nova(hospede, quarto, ini, fim, qtd, st) AS (VALUES
  (1, '101',  10, 13, 2, 'PENDENTE'),
  (2, '102',   3,  6, 2, 'CONFIRMADA'),
  (3, '103',  -1,  2, 2, 'CONFIRMADA'),     -- cobre hoje: quarto RESERVADO
  (4, '202',  -2,  1, 2, 'EM_ANDAMENTO'),   -- hospedado agora: quarto OCUPADO
  (5, '201',  20, 25, 2, 'CONFIRMADA'),
  (6, '301',  30, 33, 4, 'PENDENTE'))
INSERT INTO reserva (hospede_id, acomodacao_id, data_entrada, data_saida, qtd_hospedes, status,
                     valor_diaria, valor_total, criada_por, confirmada_em, checkin_em)
SELECT n.hospede, a.id, CURRENT_DATE + n.ini, CURRENT_DATE + n.fim, n.qtd, n.st,
       a.valor_diaria, a.valor_diaria * (n.fim - n.ini), 1,
       CASE WHEN n.st IN ('CONFIRMADA', 'EM_ANDAMENTO') THEN now() END,
       CASE WHEN n.st = 'EM_ANDAMENTO' THEN now() END
FROM nova n JOIN acomodacao a ON a.numero = n.quarto;

INSERT INTO reserva (hospede_id, acomodacao_id, data_entrada, data_saida, qtd_hospedes, status,
                     valor_diaria, valor_total, motivo_cancelamento, criada_por, cancelada_em)
SELECT 1, a.id, CURRENT_DATE + 7, CURRENT_DATE + 9, 2, 'CANCELADA',
       a.valor_diaria, a.valor_diaria * 2, 'Hóspede desistiu da viagem', 1, now()
FROM acomodacao a WHERE a.numero = '101';

UPDATE acomodacao SET status = 'RESERVADO' WHERE numero = '103';
UPDATE acomodacao SET status = 'OCUPADO'   WHERE numero = '202';
