FROM python:3.12.6-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y \
  postgresql-client \
  libpq-dev \
  python3-dev \
  build-essential \
  gcc \
  g++


# Создание рабочей директории
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копирование приложения
COPY . .

# Настройка PostgreSQL
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=451df62g956
ENV POSTGRES_DB=documents_db

# Создание пользователя и базы данных


# Запуск сервера Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]