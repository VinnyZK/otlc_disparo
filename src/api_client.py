import aiohttp
import asyncio
from typing import List, Dict
from src.config import API_TOKEN

# Tentativa de obter as variáveis do config, com fallback para o .env se não encontrar
try:
    from src.config import API_BASE_URL, API_ENDPOINT
except ImportError:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    API_BASE_URL = os.getenv("API_BASE_URL")
    API_ENDPOINT = os.getenv("API_ENDPOINT")

class OraAPIClient:
    def __init__(self):
        self.token = API_TOKEN
        self.base_url = API_BASE_URL
        self.endpoint = API_ENDPOINT
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
    async def fetch_page(self, session: aiohttp.ClientSession, page: int) -> Dict:
        """Busca uma página específica da API"""
        url = f"{self.base_url}{self.endpoint}"
        data = {
            "onlyActiveContracts": True,
            "page": page,
            "pageSize": 100  # Aumentamos para 100 para ser mais rápido
        }
        
        try:
            async with session.post(url, json=data, headers=self.headers, ssl=False) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    print(f"❌ Erro na página {page}: Status {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Erro ao buscar página {page}: {str(e)}")
            return None
    
    async def get_total_pages(self) -> int:
        """Busca a primeira página para descobrir o total"""
        async with aiohttp.ClientSession() as session:
            result = await self.fetch_page(session, 1)
            if result and 'response' in result:
                total_pages = result['response']['totalPages']
                total_records = result['response']['totalRecords']
                print(f"📊 Total de registros: {total_records}")
                print(f"📄 Total de páginas: {total_pages}")
                return total_pages
            return 0
    
    async def fetch_all_contracts(self) -> List[Dict]:
        """Busca todos os contratos de todas as páginas"""
        # Primeiro, descobrir quantas páginas existem
        total_pages = await self.get_total_pages()
        if not total_pages:
            print("❌ Não foi possível obter o total de páginas")
            return []
        
        all_contracts = []
        
        async with aiohttp.ClientSession() as session:
            # Processar em lotes de 10 páginas por vez
            batch_size = 10
            
            for start_page in range(1, total_pages + 1, batch_size):
                end_page = min(start_page + batch_size - 1, total_pages)
                
                # Criar tasks para o lote atual
                tasks = [
                    self.fetch_page(session, page)
                    for page in range(start_page, end_page + 1)
                ]
                
                # Executar lote
                results = await asyncio.gather(*tasks)
                
                # Processar resultados
                for result in results:
                    if result and 'response' in result and 'data' in result['response']:
                        all_contracts.extend(result['response']['data'])
                
                # Progresso
                print(f"✅ Processadas páginas {start_page} a {end_page} de {total_pages}")
                print(f"📦 Total de contratos baixados até agora: {len(all_contracts)}")
                
                # Pequena pausa para não sobrecarregar a API
                if end_page < total_pages:
                    await asyncio.sleep(0.5)
        
        return all_contracts
