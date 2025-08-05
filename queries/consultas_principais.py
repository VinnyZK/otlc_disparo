import asyncio
import asyncpg
import sys
import os

# Adicionar o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import DB_CONFIG

async def query_contracts_for_billing(billing_day: int):
    """
    Busca no banco de dados os contratos cujo dia de vencimento
    corresponde ao dia informado.
    """
    print(f"🚀 Buscando contratos com vencimento no dia {billing_day}...")
    
    conn = None
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        query = """
            SELECT 
                id,
                client_name,
                total_amount,
                contract_status
            FROM 
                contratos
            WHERE 
                collection_day = $1
        """
        
        results = await conn.fetch(query, billing_day)
        
        if not results:
            print(f"✅ Nenhum contrato encontrado com vencimento no dia {billing_day}.")
            return

        print(f"✅ {len(results)} contratos encontrados para o dia {billing_day}:")
        print("-" * 50)
        for record in results:
            status_map = {1: "Ativo", 2: "Cancelado", 3: "Suspenso"}
            status_text = status_map.get(record['contract_status'], "Desconhecido")
            
            print(f"  ID: {record['id']}")
            print(f"  Cliente: {record['client_name']}")
            print(f"  Valor: R$ {record['total_amount']:.2f}")
            print(f"  Status: {status_text} ({record['contract_status']})")
            print("-" * 20)
            
    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ ERRO DE BANCO DE DADOS: {e}")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")
    finally:
        if conn:
            await conn.close()

async def main():
    """
    Ponto de entrada do script.
    Executa as consultas para os dias de cobrança principais.
    """
    dias_de_cobranca_principais = [6, 16, 26]
    
    print("="*60)
    print("🔍 INICIANDO CONSULTAS PARA OS DIAS DE COBRANÇA PRINCIPAIS")
    print("="*60)
    
    for dia in dias_de_cobranca_principais:
        await query_contracts_for_billing(dia)
        print("="*60)

if __name__ == "__main__":
    from dotenv import load_dotenv
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv(dotenv_path=dotenv_path)
    asyncio.run(main())
