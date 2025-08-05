import requests

def test_form_submission():
    """
    Envia uma requisição POST para a aplicação Flask para testar
    a busca por contratos com vencimento no dia 6.
    """
    url = "http://127.0.0.1:5001/"
    data = {'dia': '6'}
    
    print(f"🚀 Enviando requisição POST para {url} com os dados: {data}")
    
    try:
        response = requests.post(url, data=data)
        
        print(f"✅ Resposta recebida com status: {response.status_code}")
        
        if response.status_code == 200:
            # Verificar se a resposta contém o HTML esperado
            if "Encontrados" in response.text and "contratos para o dia 6" in response.text:
                print("✅ SUCESSO: A página de resultados foi carregada corretamente.")
                print("   A lógica do backend e a conexão com o banco de dados estão funcionando!")
            elif "Nenhum contrato encontrado" in response.text:
                print("✅ SUCESSO: A busca funcionou, mas não há contratos para o dia 6.")
            else:
                print("❌ FALHA: A página foi carregada, mas o conteúdo esperado não foi encontrado.")
                print("   Verifique os logs do servidor Flask para mais detalhes.")
        else:
            print(f"❌ FALHA: A requisição falhou com o status {response.status_code}.")

    except requests.exceptions.ConnectionError as e:
        print(f"❌ FALHA DE CONEXÃO: Não foi possível conectar a {url}.")
        print("   Verifique se a aplicação Flask (app.py) está em execução.")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    test_form_submission()
