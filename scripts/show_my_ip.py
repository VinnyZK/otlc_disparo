import requests

def get_public_ip():
    """
    Busca e exibe o endereço de IP público da máquina atual.
    """
    print("🌐 Buscando seu endereço de IP público...")
    try:
        # Usamos um serviço externo confiável para obter o IP
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()  # Lança um erro para status ruins (4xx ou 5xx)
        
        ip_data = response.json()
        public_ip = ip_data.get('ip')
        
        if public_ip:
            print("\n" + "="*60)
            print(f"  Seu endereço de IP público é: {public_ip}")
            print("="*60)
            print("\n📋 AÇÃO NECESSÁRIA:")
            print("  1. Copie este endereço de IP.")
            print("  2. Envie para o administrador do servidor de banco de dados.")
            print("  3. Peça para que ele libere o acesso deste IP no firewall do servidor.")
            print("     Isso permitirá que tanto seus scripts locais quanto o N8N se conectem.")
        else:
            print("❌ Não foi possível determinar seu endereço de IP.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Ocorreu um erro ao tentar buscar o IP: {e}")
        print("   Verifique sua conexão com a internet.")

if __name__ == "__main__":
    get_public_ip()
