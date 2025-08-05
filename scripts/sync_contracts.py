import asyncio
import json
import asyncpg
import sys
import os

# Adicionar o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import DB_CONFIG
from src.database import create_tables, save_contracts, remove_inactive_contracts

async def drop_existing_table(conn):
    """Remove a tabela de contratos se ela já existir."""
    print("🔎 Verificando se a tabela 'contratos' antiga existe para recriação...")
    await conn.execute("DROP TABLE IF EXISTS contratos CASCADE")
    print("✅ Tabela 'contratos' antiga removida (se existia).")

async def main():
    """
    Orquestra a sincronização completa dos contratos do arquivo JSON para o banco de dados.
    """
    print("="*60)
    print("🚀 INICIANDO PROCESSO DE SINCRONIZAÇÃO COMPLETA DO BANCO DE DADOS")
    print("="*60)

    # 1. Carregar dados do arquivo JSON
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'contratos_ativos.json'))
    print(f"\n[ETAPA 1 de 4] Carregando dados de '{json_path}'...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            contratos_json = json.load(f)
        print(f"📄 {len(contratos_json)} contratos carregados.")
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo '{json_path}' não encontrado.")
        print("   Por favor, execute o script 'baixar_contratos.py' primeiro.")
        return
    except json.JSONDecodeError:
        print(f"❌ ERRO: O arquivo '{json_path}' está mal formatado ou vazio.")
        return

    if not contratos_json:
        print("⚠️ AVISO: O arquivo JSON está vazio. Nenhum dado para sincronizar.")
        return

    conn = None
    try:
        # Conectar ao banco de dados
        print("\n🔌 Conectando ao banco de dados...")
        conn = await asyncpg.connect(**DB_CONFIG)
        print(f"✅ Conexão com o banco '{DB_CONFIG['database']}' estabelecida!")

        # 2. Recriar a tabela usando a estrutura correta de database.py
        print("\n[ETAPA 2 de 4] Configurando a estrutura do banco de dados...")
        await drop_existing_table(conn) # Garante que estamos usando a estrutura correta
        await create_tables() # Usa a função do database.py
        print("✅ Estrutura do banco de dados pronta.")

        # 3. Salvar/Atualizar contratos
        print("\n[ETAPA 3 de 4] Salvando e atualizando contratos no banco...")
        saved_count = await save_contracts(contratos_json)
        print(f"✅ {saved_count} contratos foram inseridos/atualizados.")

        # 4. Remover contratos inativos
        print("\n[ETAPA 4 de 4] Removendo contratos inativos do banco...")
        active_ids = [c['id'] for c in contratos_json]
        deleted_count = await remove_inactive_contracts(active_ids)
        print(f"✅ {deleted_count} contratos inativos foram removidos.")

    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ ERRO DE BANCO DE DADOS: {e}")
        print("   Verifique as configurações de conexão e se o banco de dados está acessível.")
    except OSError as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
        print("   Não foi possível conectar ao endereço do banco de dados.")
    finally:
        if conn and not conn.is_closed():
            await conn.close()
            print("\n🔌 Conexão com o banco de dados fechada.")

    print("\n" + "="*60)
    print("🎉 PROCESSO DE SINCRONIZAÇÃO CONCLUÍDO COM SUCESSO!")
    print("="*60)

if __name__ == "__main__":
    # Carregar variáveis de ambiente do .env
    from dotenv import load_dotenv
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv(dotenv_path=dotenv_path)
    asyncio.run(main())
