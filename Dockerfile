FROM python:3.14

# Рабочая директория внутри контейнера
WORKDIR /app

# Сначала зависимости (лучший кеш Docker)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Потом код приложения
COPY . .

# Открываем порт (по желанию, для читаемости)
EXPOSE 8000

# Команда запуска uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
