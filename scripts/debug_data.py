import asyncio
import asyncpg
import sys
import os

# Adicionar o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import DB_CONFIG

async def debug_database_data():
    """
    Executa uma série de consultas de diagnóstico para entender o estado dos dados na tabela 'contratos'.
    """
    print("🚀 Conectando ao banco de dados para depurar os dados...")
    
    conn = None
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Conexão estabelecida com sucesso!")

        print("\n" + "="*50)
        print("📊 ANÁLISE DOS DADOS DA TABELA 'contratos'")
        print("="*50)

        # 1. Contagem total de registros
        total_rows = await conn.fetchval("SELECT COUNT(*) FROM contratos;")
        print(f"\n1. Total de contratos na tabela: {total_rows}")

        # 2. Contagem de contratos com dia de cobrança = 16
        day_16_count = await conn.fetchval("SELECT COUNT(*) FROM contratos WHERE collection_day = 16;")
        print(f"2. Contratos com dia de cobrança 16 (qualquer status): {day_16_count}")

        # 3. Distribuição de status dos contratos
        print("3. Distribuição de status de contrato (geral):")
        status_distribution = await conn.fetch("""
            SELECT contract_status, COUNT(*) as total
            FROM contratos
            GROUP BY contract_status
            ORDER BY contract_status;
        """)
        if not status_distribution:
            print("   - Nenhuma informação de status encontrada.")
        else:
            status_map = {1: "Ativo", 2: "Cancelado", 3: "Suspenso"}
            for record in status_distribution:
                status_text = status_map.get(record['contract_status'], "Desconhecido")
                print(f"   - Status {record['contract_status']} ({status_text}): {record['total']} contratos")

        # 4. Contagem específica da query do N8N
        n8n_query_count = await conn.fetchval("""
            SELECT COUNT(*) FROM contratos WHERE collection_day = 16 AND contract_status = 1;
        """)
        print(f"\n4. Resultado da query exata do N8N (dia 16 e status Ativo): {n8n_query_count} contratos")
        
        print("\n" + "="*50)
        print("✨ CONCLUSÃO DO DIAGNÓSTICO:")
        if n8n_query_count == 0:
            if day_16_count > 0:
                print("   - Existem contratos para o dia 16, mas nenhum deles está com o status 'Ativo' (1).")
                print("   - Verifique se os status dos contratos estão corretos na origem dos dados.")
            else:
                print("   - Simplesmente não há contratos com vencimento no dia 16 na base de dados.")
        else:
            print(f"   - A query deveria retornar {n8n_query_count} resultados. Se o N8N mostra vazio, pode ser um problema de cache ou configuração no N8N.")

    except Exception as e:
        print(f"❌ Ocorreu um erro durante o diagnóstico: {e}")
    finally:
        if conn:
            await conn.close()
            print("\n🔌 Conexão fechada.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv(dotenv_path=dotenv_path)
    asyncio.run(debug_database_data())
