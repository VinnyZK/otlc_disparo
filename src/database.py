import asyncpg
import json
from src.config import DB_CONFIG

async def create_database():
    """Cria o banco de dados se não existir"""
    # Conectar ao postgres (banco padrão)
    conn = await asyncpg.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database='postgres'
    )
    
    # Verificar se o banco existe
    exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = $1",
        DB_CONFIG['database']
    )
    
    if not exists:
        await conn.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
        print(f"✅ Banco de dados '{DB_CONFIG['database']}' criado!")
    else:
        print(f"ℹ️ Banco de dados '{DB_CONFIG['database']}' já existe.")
    
    await conn.close()

async def create_tables():
    """Cria as tabelas necessárias"""
    conn = await asyncpg.connect(**DB_CONFIG)
    
    # Criar tabela principal
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS contratos (
            id INTEGER PRIMARY KEY,
            contract_number VARCHAR(50) UNIQUE,
            client_cpf VARCHAR(14),
            client_name VARCHAR(255),
            client_email VARCHAR(255),
            collection_day INTEGER,
            contract_status INTEGER,
            total_amount DECIMAL(10,2),
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Criar índices
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_client_cpf ON contratos(client_cpf)",
        "CREATE INDEX IF NOT EXISTS idx_collection_day ON contratos(collection_day)",
        "CREATE INDEX IF NOT EXISTS idx_contract_status ON contratos(contract_status)",
        "CREATE INDEX IF NOT EXISTS idx_client_email ON contratos(client_email)",
        "CREATE INDEX IF NOT EXISTS idx_data_gin ON contratos USING GIN(data)"
    ]
    
    for index in indices:
        await conn.execute(index)
    
    print("✅ Tabelas e índices criados com sucesso!")
    
    await conn.close()

async def save_contracts(contracts):
    """Salva os contratos no banco de dados"""
    conn = await asyncpg.connect(**DB_CONFIG)
    
    # Preparar dados para inserção
    values = []
    for contract in contracts:
        # Calcular valor total dos serviços
        total = sum(
            float(service.get('amount', 0))
            for service in contract.get('servicesInformation', [])
        )
        
        values.append((
            contract['id'],
            contract.get('contractNumber'),
            contract.get('clientInformation', {}).get('clientTxId'),
            contract.get('clientInformation', {}).get('name'),
            contract.get('clientInformation', {}).get('email'),
            contract.get('collectionDay'),
            contract.get('contractStatus'),
            total,
            json.dumps(contract)
        ))
    
    # Inserir ou atualizar em lotes
    await conn.executemany("""
        INSERT INTO contratos 
        (id, contract_number, client_cpf, client_name, client_email, 
         collection_day, contract_status, total_amount, data)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
        ON CONFLICT (id) 
        DO UPDATE SET 
            contract_number = EXCLUDED.contract_number,
            client_cpf = EXCLUDED.client_cpf,
            client_name = EXCLUDED.client_name,
            client_email = EXCLUDED.client_email,
            collection_day = EXCLUDED.collection_day,
            contract_status = EXCLUDED.contract_status,
            total_amount = EXCLUDED.total_amount,
            data = EXCLUDED.data,
            updated_at = NOW()
    """, values)
    
    await conn.close()
    return len(values)

async def remove_inactive_contracts(active_ids):
    """Remove contratos que não estão mais ativos"""
    conn = await asyncpg.connect(**DB_CONFIG)
    
    deleted = await conn.fetchval("""
        WITH deleted AS (
            DELETE FROM contratos 
            WHERE id != ALL($1::int[])
            RETURNING 1
        )
        SELECT COUNT(*) FROM deleted
    """, active_ids)
    
    await conn.close()
    return deleted or 0
