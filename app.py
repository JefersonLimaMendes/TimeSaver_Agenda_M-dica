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


def _is_authenticated():
    return 'user_id' in session


def _normalize_agendamento_payload(payload):
    required_fields = [
        'data', 'horario', 'paciente', 'cpf',
        'medico', 'especialidade', 'convenio', 'status'
    ]

    normalized = {}
    for field in required_fields:
        value = payload.get(field, '') if isinstance(payload, dict) else ''
        normalized[field] = value.strip() if isinstance(value, str) else ''

    missing = [field for field in required_fields if not normalized[field]]
    return normalized, missing

@app.route('/', methods=['GET'])
def index():
    if not _is_authenticated():
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
    if not _is_authenticated():
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


@app.route('/api/agendamentos', methods=['GET'])
def listar_agendamentos_locais():
    if not _is_authenticated():
        return jsonify({'error': 'Não autorizado'}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Falha ao conectar com o banco de dados.'}), 500

    rows = conn.execute(
        '''
        SELECT id, data, horario, paciente, cpf, medico, especialidade, convenio, status
        FROM agendamentos
        ORDER BY id DESC
        '''
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route('/api/agendamentos', methods=['POST'])
def cadastrar_agendamento_local():
    if not _is_authenticated():
        return jsonify({'error': 'Não autorizado'}), 401

    payload = request.get_json(silent=True) or {}
    agendamento, missing_fields = _normalize_agendamento_payload(payload)

    if missing_fields:
        return jsonify({
            'error': 'Campos obrigatórios ausentes.',
            'missing_fields': missing_fields
        }), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Falha ao conectar com o banco de dados.'}), 500

    cursor = conn.execute(
        '''
        INSERT INTO agendamentos (data, horario, paciente, cpf, medico, especialidade, convenio, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            agendamento['data'],
            agendamento['horario'],
            agendamento['paciente'],
            agendamento['cpf'],
            agendamento['medico'],
            agendamento['especialidade'],
            agendamento['convenio'],
            agendamento['status']
        )
    )
    conn.commit()
    agendamento['id'] = cursor.lastrowid
    conn.close()

    return jsonify(agendamento), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)