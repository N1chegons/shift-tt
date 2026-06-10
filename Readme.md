# Test task for shift

Тестовое задание для ШИФТ. Сервис для бронирования переговорных комнат.

## 🛠 Технологии
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-24.0-2496ED?logo=docker)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2.21-2496ED)

## Быстрый старт

## Установка и запуск

### 1. Клонируйте репозиторий
git clone https://github.com/N1chegons/shift-tt.git
cd <папка-проекта>

### 2. Создайте файл окружения
.env (на основе файла .env.example)

### 3. Запустите приложение
```
docker-compose up --build
```

### 4. Откройте в браузере
-  Документация: http://localhost:5050/docs
-  ReDoc: http://localhost:5050/redoc

## Запуск тестов
### Запустите тестовую базу данных
```
docker compose -f docker-compose-test.yml up -d
```
### Запустите тесты
```
pytest -s -v
```

📞 Контакты
@Nichegons - nichegons@gmail.com

