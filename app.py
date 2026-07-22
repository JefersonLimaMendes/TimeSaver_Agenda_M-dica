from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import requests
import os
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave_secreta_padrao')
API_URL = os.environ.get('API_URL', 'http://localhost:5001/api/agendamentos')

# Configuração de logs para facilitar identificação de problemas
logging.basicConfig(level=logging.INFO)

def get_db_connection():
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        app.logger.error(f"Erro ao conectar com o banco de dados: {e}")
        return None

@app.route('/', methods=['GET'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        if not conn:
            flash('Erro interno: Não foi possível conectar ao banco de dados.', 'danger')
            return render_template('login.html')

        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                            (username, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas. Verifique seu usuário e senha.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/api/proxy/agendamentos', methods=['GET'])
def proxy_agendamentos():
    """Proxy para buscar dados da API externa e tratar falhas graciosamente."""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Validar resposta vazia
        if not data:
            return jsonify({'warning': 'Nenhum agendamento encontrado no momento.'}), 200
            
        return jsonify(data)
        
    except requests.exceptions.ConnectionError:
        app.logger.error("Erro: Falha de conexão com a API de agendamentos.")
        return jsonify({'error': 'Serviço de agendamentos temporariamente indisponível.'}), 503
    except requests.exceptions.Timeout:
        app.logger.error("Erro: Tempo de resposta da API excedido.")
        return jsonify({'error': 'A API demorou muito para responder.'}), 504
    except ValueError:
        app.logger.error("Erro: Resposta inválida (não é JSON) recebida da API.")
        return jsonify({'error': 'Resposta inválida do serviço de agendamentos.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)