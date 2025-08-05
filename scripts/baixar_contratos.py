import asyncio
import json
import sys
import os

# Adicionar o diretório raiz ao sys.path para encontrar a pasta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_client import OraAPIClient

async def main():
    """
    Orquestra o download de todos os contratos ativos da API
    e salva o resultado em um arquivo JSON na raiz do projeto.
    """
    print("🚀 INICIANDO DOWNLOAD DOS CONTRATOS ATIVOS...")
    
    client = OraAPIClient()
    
    # 1. Buscar todos os contratos usando o cliente da API
    todos_contratos = await client.fetch_all_contracts()
    
    if not todos_contratos:
        print("❌ Nenhum contrato foi baixado. O processo será encerrado.")
        return

    # 2. Salvar em arquivo JSON na raiz do projeto
    output_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'contratos_ativos.json'))
    print(f"\n💾 Salvando {len(todos_contratos)} contratos em '{output_filename}'...")
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(todos_contratos, f, indent=4, ensure_ascii=False)
        print(f"✅ Arquivo '{output_filename}' salvo com sucesso!")
    except IOError as e:
        print(f"❌ Erro ao salvar o arquivo JSON: {e}")

    print("\n🎉 PROCESSO DE DOWNLOAD CONCLUÍDO!")

if __name__ == "__main__":
    # Carregar variáveis de ambiente do .env
    from dotenv import load_dotenv
    # O .env deve estar na raiz do projeto
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv(dotenv_path=dotenv_path)
    
    asyncio.run(main())
