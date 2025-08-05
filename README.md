# Sistema de Faturamento e Consulta de Contratos ORA Telecom

Este projeto automatiza o processo de download, armazenamento e consulta de contratos ativos da ORA Telecom, fornecendo uma solução completa para a gestão de faturamento.

## Funcionalidades

- **Download Automatizado**: Baixa todos os contratos ativos da API da ORA Telecom.
- **Sincronização com Banco de Dados**: Armazena os dados em um banco de dados PostgreSQL, com uma estrutura otimizada para consultas.
- **Interface Web**: Uma "telinha" simples para consultar contratos com vencimento em um dia específico.
- **Estrutura Organizada**: O código é modular e organizado em pastas para fácil manutenção.
- **Queries para Automação**: Inclui queries SQL prontas para serem usadas em ferramentas como o N8N.

## Estrutura do Projeto

```
.
├── app.py                  # Aplicação web Flask
├── queries/                # Scripts de consulta SQL
│   ├── consultas_diarias.py
│   ├── consultas_principais.py
│   └── n8n_queries.sql
├── scripts/                # Scripts de automação
│   ├── baixar_contratos.py
│   ├── sync_contracts.py
│   └── test_connection.py
├── src/                    # Código-fonte principal
│   ├── api_client.py
│   ├── config.py
│   └── database.py
├── templates/              # Arquivos HTML para a aplicação web
│   └── index.html
├── .env.example            # Exemplo de arquivo de ambiente
├── .gitignore              # Arquivos a serem ignorados pelo Git
├── requirements.txt        # Dependências do projeto
└── README.md               # Esta documentação
```

## Como Configurar e Usar

### 1. Pré-requisitos

- Python 3.10+
- Um banco de dados PostgreSQL acessível.
- Credenciais da API da ORA Telecom.

### 2. Instalação

**a. Clone o repositório:**
```bash
git clone https://github.com/VinnyZK/otlc_disparo.git
cd otlc_disparo
```

**b. Crie e ative um ambiente virtual (recomendado):**
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

**c. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**d. Configure as variáveis de ambiente:**
Renomeie o arquivo `.env.example` para `.env` e preencha com suas credenciais:
```dotenv
# .env
API_TOKEN="SEU_TOKEN_DA_API_AQUI"

# Configurações do PostgreSQL
DB_HOST="endereco_do_seu_banco"
DB_PORT=5432
DB_NAME="nome_do_banco"
DB_USER="usuario_do_banco"
DB_PASSWORD="senha_do_banco"

# Configurações da API (geralmente não precisam ser alteradas)
API_BASE_URL=https://erp.oratelecom.com.br:45715
API_ENDPOINT=/external/integrations/thirdparty/contract/getpaged
```

### 3. Fluxo de Trabalho

**a. Testar as Conexões (Opcional, mas recomendado):**
Verifique se o sistema consegue se conectar à API e ao banco de dados.
```bash
python scripts/test_connection.py
```

**b. Baixar os Contratos:**
Este script busca todos os contratos na API e salva em um arquivo `contratos_ativos.json`.
```bash
python scripts/baixar_contratos.py
```

**c. Sincronizar com o Banco de Dados:**
Este script lê o arquivo `contratos_ativos.json` e insere/atualiza os dados no seu banco de dados PostgreSQL.
```bash
python scripts/sync_contracts.py
```

### 4. Usando a Interface Web

Para consultar os vencimentos de forma interativa, inicie a aplicação Flask:
```bash
python app.py
```
Abra seu navegador e acesse `http://127.0.0.1:5001`.

### 5. Usando as Queries

- **`queries/consultas_diarias.py`**: Pode ser executado para buscar os vencimentos de um dia específico.
  ```bash
  # Busca os vencimentos do dia atual
  python queries/consultas_diarias.py

  # Busca os vencimentos do dia 15
  python queries/consultas_diarias.py 15
  ```
- **`queries/consultas_principais.py`**: Executa as buscas para os dias 6, 16 e 26.
  ```bash
  python queries/consultas_principais.py
  ```
- **`queries/n8n_queries.sql`**: Contém as queries prontas para serem usadas em ferramentas de automação como o N8N.
