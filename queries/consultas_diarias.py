import asyncio
import asyncpg
import sys
import os
from datetime import date

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
        
        # A query usa o campo 'collection_day' que foi extraído para uma coluna própria.
        # Isso é muito mais rápido do que consultar dentro do JSONB.
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

        print(f"✅ {len(results)} contratos encontrados:")
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
    Verifica se um dia foi passado como argumento, senão usa o dia de hoje.
    """
    # Pega o dia do argumento da linha de comando, se existir.
    # Ex: python queries/consultas_diarias.py 15
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        day_to_query = int(sys.argv[1])
        if not 1 <= day_to_query <= 31:
            print("❌ Erro: O dia deve ser um número entre 1 e 31.")
            return
        print(f"🔎 Usando o dia fornecido pelo argumento: {day_to_query}")
    else:
        # Se nenhum argumento for passado, usa o dia atual.
        day_to_query = date.today().day
        print(f"🔎 Nenhum dia especificado. Usando o dia de hoje: {day_to_query}")
    
    await query_contracts_for_billing(day_to_query)


if __name__ == "__main__":
    from dotenv import load_dotenv
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv(dotenv_path=dotenv_path)
    asyncio.run(main())
