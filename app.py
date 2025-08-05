import os
import psycopg2
from flask import Flask, render_template, request, flash
from src.config import SYNC_DB_CONFIG # Importar a configuração síncrona

app = Flask(__name__)
app.secret_key = os.urandom(24) # Necessário para usar flash messages

def get_db_connection():
    """Cria uma conexão com o banco de dados usando a config centralizada."""
    try:
        # Usar o dicionário de configuração diretamente
        conn = psycopg2.connect(**SYNC_DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        # Retorna None se a conexão falhar
        print(f"Erro de conexão com o banco de dados: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    contratos = []
    dia_pesquisado = None

    if request.method == 'POST':
        dia_pesquisado = request.form.get('dia')
        
        if not dia_pesquisado or not dia_pesquisado.isdigit():
            flash('Por favor, insira um número de dia válido.', 'error')
            return render_template('index.html', contratos=contratos, dia_pesquisado=None)

        dia = int(dia_pesquisado)
        if not 1 <= dia <= 31:
            flash('O dia deve ser um número entre 1 e 31.', 'error')
            return render_template('index.html', contratos=contratos, dia_pesquisado=dia)

        conn = get_db_connection()
        if conn is None:
            flash('Não foi possível conectar ao banco de dados. Verifique as configurações e a conexão.', 'error')
            return render_template('index.html', contratos=[], dia_pesquisado=dia)

        try:
            with conn.cursor() as cur:
                query = """
                    SELECT 
                        id,
                        client_name,
                        total_amount,
                        contract_status
                    FROM 
                        contratos
                    WHERE 
                        collection_day = %s
                    ORDER BY
                        client_name;
                """
                cur.execute(query, (dia,))
                results = cur.fetchall()
                
                # Mapear status para texto
                status_map = {1: "Ativo", 2: "Cancelado", 3: "Suspenso"}
                
                # Converter resultados para uma lista de dicionários
                for row in results:
                    contratos.append({
                        'id': row[0],
                        'client_name': row[1],
                        'total_amount': f"{row[2]:.2f}",
                        'status': status_map.get(row[3], f"Desconhecido ({row[3]})")
                    })
            
            if not contratos:
                flash(f'Nenhum contrato encontrado com vencimento no dia {dia}.', 'info')

        except psycopg2.Error as e:
            flash(f'Ocorreu um erro ao consultar o banco de dados: {e}', 'error')
        finally:
            if conn:
                conn.close()

    return render_template('index.html', contratos=contratos, dia_pesquisado=dia_pesquisado)

if __name__ == '__main__':
    # O modo debug recarrega o servidor automaticamente a cada mudança no código
    app.run(debug=True, port=5001)
