import asyncio
import asyncpg
import sys
import os

# Adicionar o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import DB_CONFIG

async def check_schema():
    """
    Conecta ao banco de dados e lista todas as tabelas no schema 'public'.
    """
    print("🚀 Conectando ao banco de dados para verificar o schema...")
    
    conn = None
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        db_name = await conn.fetchval("SELECT current_database()")
        print(f"✅ Conectado com sucesso ao banco: '{db_name}'")
        
        print("\n🔍 Buscando tabelas no schema 'public'...")
        tables = await conn.fetch("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        if not tables:
            print("❌ Nenhuma tabela encontrada no schema 'public'.")
            print("   Isso é inesperado. Por favor, execute o script 'sync_contracts.py' novamente.")
            return

        print(f"✅ {len(tables)} tabelas encontradas:")
        for i, record in enumerate(tables):
            table_name = record['tablename']
            print(f"  {i+1}. {table_name}")
            if table_name == 'contratos':
                print("      -> Tabela 'contratos' encontrada! 👍")

        if 'contratos' not in [r['tablename'] for r in tables]:
             print("\n❌ AVISO: A tabela 'contratos' não foi encontrada. Execute 'scripts/sync_contracts.py'.")
        else:
            print("\n✨ CONCLUSÃO: A tabela 'contratos' existe no banco de dados. O problema provavelmente está na configuração de credenciais do N8N.")

    except Exception as e:
        print(f"❌ Ocorreu um erro ao tentar conectar ou verificar o banco de dados: {e}")
    finally:
        if conn:
            await conn.close()
            print("\n🔌 Conexão fechada.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv(dotenv_path=dotenv_path)
    asyncio.run(check_schema())
