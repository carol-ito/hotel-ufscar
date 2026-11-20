-- Hotel UFSCar - administrador (perfil GESTAO).
-- Idempotente: pode rodar quantas vezes quiser; se o e-mail ja existir, atualiza nome, senha e perfil.
-- A senha NAO fica em texto: abaixo vai apenas o hash bcrypt.
-- Docker Compose: roda sozinho na primeira subida (03-admin.sql). Em banco ja criado, rode manualmente:
--   Get-Content db\admin.sql | docker compose exec -T db psql -U hotel -d hotel

INSERT INTO usuario (nome, email, senha_hash, perfil, ativo) VALUES
  ('carol-ito', 'carolineito18@gmail.com', '$2b$12$hHVG4it.1ilKyKgYvXKxZO4kY80EOba.urfwHtbWv5wy9BTFCzqpm', 'GESTAO', TRUE)
ON CONFLICT ((lower(email))) DO UPDATE
  SET nome = EXCLUDED.nome, senha_hash = EXCLUDED.senha_hash, perfil = 'GESTAO', ativo = TRUE;
