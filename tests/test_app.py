import sys
import os
import pytest

# Adiciona a raiz ao PATH para evitar erro de importação do app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from init_db import init as init_db

@pytest.fixture
def client():
    # Garante que o banco de dados e as tabelas existam antes dos testes
    init_db()
    
    app.config['TESTING'] = True
    app.secret_key = 'test_key'
    
    with app.test_client() as client:
        yield client

def test_acesso_negado_sem_login(client):
    """Garante que a agenda não abre sem login"""
    response = client.get('/')
    assert response.status_code == 302
    assert b'/login' in response.data

def test_login_invalido(client):
    """Garante que o erro é tratado ao usar credenciais incorretas"""
    response = client.post('/login', data={'username': 'errado', 'password': '123'})
    assert response.status_code == 200
    assert b'Credenciais' in response.data


def test_cadastro_agendamento_sem_login(client):
    response = client.post('/api/agendamentos', json={
        'data': '30/07/2026',
        'horario': '10:00',
        'paciente': 'Teste Sem Login',
        'cpf': '123.456.789-00',
        'medico': 'Dr. Sem Sessao',
        'especialidade': 'Clínico',
        'convenio': 'Particular',
        'status': 'Pendente'
    })

    assert response.status_code == 401


def test_cadastro_e_listagem_agendamento_com_login(client):
    login_response = client.post(
        '/login',
        data={'username': 'admin', 'password': 'admin123'},
        follow_redirects=False
    )
    assert login_response.status_code == 302

    cadastro_response = client.post('/api/agendamentos', json={
        'data': '30/07/2026',
        'horario': '10:00',
        'paciente': 'Maria Teste',
        'cpf': '123.456.789-00',
        'medico': 'Dra. Helena',
        'especialidade': 'Dermatologia',
        'convenio': 'Unimed',
        'status': 'Confirmado'
    })

    assert cadastro_response.status_code == 201
    cadastro_json = cadastro_response.get_json()
    assert cadastro_json['paciente'] == 'Maria Teste'
    assert 'id' in cadastro_json

    listagem_response = client.get('/api/agendamentos')
    assert listagem_response.status_code == 200
    listagem_json = listagem_response.get_json()

    assert any(item['paciente'] == 'Maria Teste' for item in listagem_json)