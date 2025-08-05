import asyncio
import asyncpg
import aiohttp
import sys
import os

# Adicionar o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import DB_CONFIG, API_TOKEN

async def test_database():
    """Testa conexão com o banco de dados"""
    print("🔍 Testando conexão com o banco de dados...")
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        version = await conn.fetchval("SELECT version()")
        current_db = await conn.fetchval("SELECT current_database()")
        
        print(f"✅ Conectado ao banco: {current_db}")
        print(f"📌 Versão: {version}")
        
        # Verificar se tem tabelas
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        
        if tables:
            print(f"⚠️  O banco '{current_db}' já tem {len(tables)} tabelas")
        else:
            print(f"✅ O banco '{current_db}' está vazio - perfeito!")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {str(e)}")
        return False

async def test_api():
    """Testa conexão com a API"""
    print("\n🔍 Testando conexão com a API...")
    
    if not API_TOKEN or API_TOKEN == "SEU_TOKEN_AQUI":
        print("❌ Token da API não configurado no .env!")
        return False
    
    # Tentativa de obter as variáveis do config, com fallback para o .env se não encontrar
    try:
        from src.config import API_BASE_URL, API_ENDPOINT
    except ImportError:
        from dotenv import load_dotenv
        dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
        load_dotenv(dotenv_path=dotenv_path)
        API_BASE_URL = os.getenv("API_BASE_URL")
        API_ENDPOINT = os.getenv("API_ENDPOINT")

    url = f"{API_BASE_URL}{API_ENDPOINT}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    data = {
        "onlyActiveContracts": True,
        "page": 1,
        "pageSize": 1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers, ssl=False) as response:
                if response.status == 200:
                    result = await response.json()
                    total = result.get('response', {}).get('totalRecords', 0)
                    print(f"✅ API conectada! Total de contratos: {total}")
                    return True
                else:
                    print(f"❌ Erro na API: Status {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Erro ao conectar na API: {str(e)}")
        return False

async def main():
    print("=" * 60)
    print("🧪 TESTE DE CONEXÕES")
    print("=" * 60)
    
    # Testar banco
    db_ok = await test_database()
    
    # Testar API
    api_ok = await test_api()
    
    print("\n" + "=" * 60)
    if db_ok and api_ok:
        print("✅ TUDO PRONTO! Pode executar os scripts na pasta 'scripts'.")
    else:
        print("❌ Corrija os erros acima antes de continuar")
    print("=" * 60)

if __name__ == "__main__":
    from dotenv import load_dotenv
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv(dotenv_path=dotenv_path)
    asyncio.run(main())
