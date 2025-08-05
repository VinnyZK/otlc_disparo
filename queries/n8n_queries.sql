-- =================================================================
-- QUERIES PARA O NÓ "SQL QUERY" DO N8N
-- =================================================================
-- Estas queries foram desenhadas para serem usadas em workflows de
-- automação de cobrança no N8N.
-- Elas selecionam os campos mais importantes e filtram apenas
-- os contratos com status "Ativo" (contract_status = 1).
-- =================================================================


-- =================================================================
-- 1. CONSULTA DINÂMICA PARA QUALQUER DIA
-- =================================================================
-- Use esta query quando você quiser que o N8N busque os vencimentos
-- do dia em que o workflow está rodando.

-- INSTRUÇÕES:
-- 1. No seu workflow N8N, você pode usar um nó "Schedule" para rodar diariamente.
-- 2. No nó "SQL Query", cole a query abaixo.
-- 3. Substitua o '?' pelo valor dinâmico do dia. No N8N, você pode
--    usar uma expressão como: {{ $today.day }}

SELECT
    id,
    client_name,
    client_cpf,
    client_email,
    total_amount,
    contract_number
FROM
    contratos
WHERE
    collection_day = ? -- Ex: {{ $today.day }}
    AND contract_status = 1; -- Garante que apenas contratos ativos sejam retornados


-- =================================================================
-- 2. CONSULTAS PARA DIAS DE COBRANÇA PRINCIPAIS (6, 16, 26)
-- =================================================================
-- Use estas queries se você tiver workflows separados que rodam
-- especificamente nestes dias.

-- === VENCIMENTO DIA 6 ===
SELECT
    id,
    client_name,
    client_cpf,
    client_email,
    total_amount,
    contract_number
FROM
    contratos
WHERE
    collection_day = 6
    AND contract_status = 1;


-- === VENCIMENTO DIA 16 ===
SELECT
    id,
    client_name,
    client_cpf,
    client_email,
    total_amount,
    contract_number
FROM
    contratos
WHERE
    collection_day = 16
    AND contract_status = 1;


-- === VENCIMENTO DIA 26 ===
SELECT
    id,
    client_name,
    client_cpf,
    client_email,
    total_amount,
    contract_number
FROM
    contratos
WHERE
    collection_day = 26
    AND contract_status = 1;
