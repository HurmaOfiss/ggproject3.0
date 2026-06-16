FROM python:3.12-slim
WORKDIR /app

# Копируем только requirements.txt для установки зависимостей (используем кэш)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip list | grep dotenv
# Копируем всё остальное (main.py, config.py, другие модули)
COPY . .

CMD ["python", "main.py"]