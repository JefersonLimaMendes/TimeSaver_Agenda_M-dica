FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Inicializa o banco de dados e cria o usuário teste durante o build
RUN python init_db.py
EXPOSE 5000
CMD ["python", "app.py"]