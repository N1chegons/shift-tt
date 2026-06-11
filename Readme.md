# Test task for shift

Тестовое задание для ШИФТ. Сервис для бронирования переговорных комнат.

## Технологии
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-24.0-2496ED?logo=docker)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2.21-2496ED)
![FastAPI Users](https://img.shields.io/badge/FastAPI%20Users-10.x-009688)
## Быстрый старт

## Установка и запуск

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/N1chegons/shift-tt.git
cd shift-tt
```

### 2. Создайте файл окружения
.env (на основе файла .env.example)

<details>
    <summary>Структура .env.example</summary>    

    DB_HOST=db_host
    DB_PORT=5432
    DB_NAME=db_name
    DB_USER=db_user
    DB_PASS=db_pass
    
    TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/test_db
    
    JWT_KEY=your_jwt_key
    MANAGER_PASS=your_manager_pass

</details>

### 3. Запустите приложение
```bash
docker-compose up --build
```

### 4. Откройте в браузере
-  Документация: http://localhost:5050/docs
-  ReDoc: http://localhost:5050/redoc

## Запуск тестов
### Запустите тестовую базу данных
```bash
docker compose -f docker-compose-test.yml up -d
```
### Запустите тесты
```bash
pytest -s -v
```

## Пример работы

## API Endpoints - пример работы

<details>
    <summary>1. Регистраиця</summary>

Запрос
![img.png](img.png)
Ответ
![img_1.png](img_1.png)
</details>

<details>
    <summary>2. Логинг</summary>

Запрос
![img_2.png](img_2.png)
Ответ
![img_3.png](img_3.png)
</details>

<details>
    <summary>3. Получение всех доступных комнат</summary>

Ответ
![img_4.png](img_4.png)
</details>

<details>
    <summary>4. Получение свободных слотов времени у определенной переговорной комнаты</summary>

Запрос
![img_5.png](img_5.png)
Ответ
![img_6.png](img_6.png)
</details>

<details>
    <summary>5. Забронировать переговорную комнаты</summary>

Запрос
![img_7.png](img_7.png)
Ответ
![img_8.png](img_8.png)
</details>

<details>
    <summary>6. Просмотр броней пользователяы</summary>

Ответ
![img_9.png](img_9.png)
</details>

<details>
    <summary>7. Отмена брони пользователя</summary>

Запрос
![img_10.png](img_10.png)
Ответ
![img_11.png](img_11.png)
</details>

<details>
    <summary>8. Отмена всех активных броней пользователя</summary>

Ответ
![img_12.png](img_12.png)
</details>

<details>
    <summary>9. Получение прав администратора</summary>

Ответ
![img_13.png](img_13.png)
</details>

<details>
    <summary>10. Просмотр всех активных броней (Админ)</summary>

Запрос
![img_14.png](img_14.png)
Ответ
![img_15.png](img_15.png)
</details>

<details>
    <summary>11. Просмотр всех активных броней на определенную дату (Админ)</summary>

Запрос
![img_16.png](img_16.png)
Ответ
![img_17.png](img_17.png)
</details>

<details>
    <summary>12. Отмена брони (Админ)</summary>

Запрос
![img_18.png](img_18.png)
Ответ
![img_19.png](img_19.png)
</details>

<details>
    <summary>13. Отмена всех активных брони (Админ)</summary>

Ответ
![img_20.png](img_20.png)
</details>

## 📞 Контакты
#### @Nichegons - nichegons@gmail.com

