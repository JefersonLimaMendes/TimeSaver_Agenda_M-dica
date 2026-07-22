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