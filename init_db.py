import sqlite3
import os
import bcrypt

def init():
    #Remove o banco se já existir para criar um ambiente limpo
    if os.path.exists('database.db'):
        os.remove('database.db')
        
    conn = sqlite3.connect('database.db')
    
    #Criação da tabela de usuários
    conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            horario TEXT NOT NULL,
            paciente TEXT NOT NULL,
            cpf TEXT NOT NULL,
            medico TEXT NOT NULL,
            especialidade TEXT NOT NULL,
            convenio TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    
    #Inserção do usuário de teste
    # Hash da senha padrão usando bcrypt
    admin_pass = 'admin123'.encode('utf-8')
    admin_hash = bcrypt.hashpw(admin_pass, bcrypt.gensalt())
    conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', admin_hash))
    conn.commit()
    conn.close()
    print("Banco de dados 'database.db' inicializado com sucesso!")

if __name__ == '__main__':
    init()