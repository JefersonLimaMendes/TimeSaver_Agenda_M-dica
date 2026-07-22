Agenda Médica - Time Saver (Desafio Técnico)

Aplicação web desenvolvida em Python (Flask) para gestão de agendamentos médicos.

🛠️ Tecnologias Utilizadas
- Backend: Python 3.11, Flask
- Banco de Dados: SQLite
- Frontend: HTML5, Bootstrap 5, Tabulator JS
- Infraestrutura: Docker, Docker Compose
- Testes: Pytest

🧠 Decisões Técnicas e Arquitetura
1. API Simulada Isolada: Criei um serviço independente (mock_api.py) no Docker Compose para simular o comportamento de uma requisição HTTP real entre microsserviços.
2. Tratamento de Erros via Proxy: A comunicação com a API externa é feita por uma rota proxy (/api/proxy/agendamentos) no backend, impedindo que erros de timeout ou queda da API quebrem o frontend diretamente. O frontend reage amigavelmente através de alertas do Bootstrap.
3. Persistência Leve: O SQLite foi escolhido pela facilidade e por não requerer um container robusto adicional, agilizando a execução.

---

🚀 Como Executar

Você pode rodar a aplicação utilizando Docker (modo recomendado) ou localmente via ambiente virtual Python.

Opção 1: Execução com Docker (Recomendado)

O projeto está totalmente conteinerizado. Basta ter o Docker instalado e seguir os passos:

1. Abra o terminal na raiz da pasta do projeto.
2. Suba os containers executando o comando:
   ```bash
   docker-compose up --build
(Em versões mais recentes do Docker Desktop, você também pode usar docker compose up --build)
3. Acesse no navegador: http://localhost:5000

## Opção 2: Execução Local (Sem Docker)

Caso prefira rodar diretamente na sua máquina sem containers:
Crie e ative o ambiente virtual Python:

1. Windows:
    Terminal
    python -m venv venv
    .\venv\Scripts\Activate.ps1

    Se for Linux/Mac:
    python3 -m venv venv
    source venv/bin/activate

2. Instale as dependências:
    pip install -r requirements.txt

3. Inicie a API simulada e a Aplicação em terminais separados (com o venv ativo):
    Terminal 1: python mock_api.py
    Terminal 2: python app.py

4. Acesse no navegador: http://localhost:5000

🔑Credenciais para Acesso

Utilize o login de teste pré-cadastrado no banco de dados:
Usuário: admin
Senha: admin123

Para rodar os testes unitários da aplicação, execute no terminal:
python -m pytest