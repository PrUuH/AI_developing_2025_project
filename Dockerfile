# Dockerfile
FROM python:3.10-slim

# Установка зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Порт Streamlit
EXPOSE 8501

# Запуск
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=172.18.0.1"]