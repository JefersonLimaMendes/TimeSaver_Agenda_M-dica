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


def test_cadastro_manual_de_usuario(client):
    """Garante que um novo usuário pode se cadastrar manualmente e entrar."""
    response = client.post('/register', data={'username': 'novo_user', 'password': '123456'}, follow_redirects=False)
    assert response.status_code == 302

    login_response = client.post('/login', data={'username': 'novo_user', 'password': '123456'})
    assert login_response.status_code == 302


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


def test_delecao_agendamento_sem_login(client):
    response = client.delete('/api/agendamentos/1')
    assert response.status_code == 401


def test_cadastro_e_delecao_agendamento_com_login(client):
    login_response = client.post(
        '/login',
        data={'username': 'admin', 'password': 'admin123'},
        follow_redirects=False
    )
    assert login_response.status_code == 302

    cadastro_response = client.post('/api/agendamentos', json={
        'data': '31/07/2026',
        'horario': '11:00',
        'paciente': 'Paciente Delecao',
        'cpf': '000.111.222-33',
        'medico': 'Dr. Delete',
        'especialidade': 'Clínico',
        'convenio': 'Particular',
        'status': 'Pendente'
    })
    assert cadastro_response.status_code == 201
    agendamento_id = cadastro_response.get_json()['id']

    delecao_response = client.delete(f'/api/agendamentos/{agendamento_id}')
    assert delecao_response.status_code == 200

    listagem_response = client.get('/api/agendamentos')
    listagem_json = listagem_response.get_json()
    assert all(item['id'] != agendamento_id for item in listagem_json)


def test_colisao_horario_medico(client):
    # login
    login_response = client.post(
        '/login',
        data={'username': 'admin', 'password': 'admin123'},
        follow_redirects=False
    )
    assert login_response.status_code == 302

    payload = {
        'data': '01/08/2026',
        'horario': '09:00',
        'paciente': 'Paciente A',
        'cpf': '111.222.333-44',
        'medico': 'Dr. Conflito',
        'especialidade': 'Clínico',
        'convenio': 'Unimed',
        'status': 'Confirmado'
    }

    r1 = client.post('/api/agendamentos', json=payload)
    assert r1.status_code == 201

    # Tentativa com mesmo médico/data/horário deve falhar com 409
    payload2 = payload.copy()
    payload2['paciente'] = 'Paciente B'
    r2 = client.post('/api/agendamentos', json=payload2)
    assert r2.status_code == 409