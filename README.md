# Foodgram [![Main Foodgram workflow](https://github.com/dxndigiden/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/dxndigiden/foodgram-project-react/actions/workflows/main.yml)
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?style=flat&logo=django&logoColor=white)
![Django REST framework](https://img.shields.io/badge/-Django%20REST%20framework-ff9900?style=flat&logo=django&logoColor=white)
![Postman](https://img.shields.io/badge/-Postman-FF6C37?style=flat&logo=postman&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat&logo=docker&logoColor=white)

Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.


## Установка и запуск проекта

Для запуска проекта на вашем локальном компьютере выполните следующие шаги:

1. Клонируйте репозиторий на ваш компьютер:

    ```
    git clone git@github.com:Dxndigiden/foodgram-project-react.git
    ```

2. Перейдите в папку с бэкендом проекта:

    ```
    cd foodgram--project-react/foodgram
    ```

3. Создайте и активируйте виртульное окружение, установите зависимости:

    ```
    python -m venv venv
    source venv/Sripts/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

4. Примените миграции:

    ```
    python manage.py migrate
    ```

5. Создайте суперпользователя:

    ```
    python manage.py createsuperuser
    ```

6. Запустите сервер разработки:

    ```
    python manage.py runserver 0.0.0.0:8000
    ```


## Описание проекта

Foodgram - это платформа для обмена рецептами и ингредиентами. Основные функции проекта включают в себя:

- Делиться своими рецептами
- Смотреть рецепты других пользователей
- Добавлять рецепты в избранное
- Сформировать список покупок, добавляя рецепт в корзину

## Инструкция по развертыванию

1. Установите Docker и Docker Compose на вашем компьютере.
2. Склонируйте репозиторий на ваш компьютер:

    ```
    git clone git@github.com:Dxndigiden/foodgram-project-react.git
    ```

3. Перейдите в папку проекта:

    ```
    cd foodgram
    ```

4. Создайте файл .env и заполните его данными, указанными в примере ниже, либо скопируйте из .env.example.

## Пример .env файла

```
DB_NAME=your_database_name
POSTGRES_USER=your_postgres_username
POSTGRES_PASSWORD=your_postgres_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_django_secret_key

DEBUG=False
DEVELOP=False
```

5. Запустите Docker Compose:

    ```
    docker compose up -d
    ```

6. Примените миграции:

    ```
    docker compose exec web python manage.py migrate
    ```

7. Соберите статику:

    ```
    docker compose exec web python manage.py collectstatic --no-input
    docker compose exec -T backend python manage.py loaddata ingredients.json
    docker compose exec -T backend python manage.py tags_load
    ```


## Ссылки

- [Foodgram в интернете](https://foodgrambydxn.ddns.net)

## Автор

Автор: [Dxndigiden](https://github.com/dxndigiden)
