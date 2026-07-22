import sqlite3
import os

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
    
    #Inserção do usuário de teste
    conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin123'))
    conn.commit()
    conn.close()
    print("Banco de dados 'database.db' inicializado com sucesso!")

if __name__ == '__main__':
    init()