# Foodgram [![Main Foodgram workflow](https://github.com/dxndigiden/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/dxndigiden/foodgram-project-react/actions/workflows/main.yml)
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?style=flat&logo=django&logoColor=white)
![Django REST framework](https://img.shields.io/badge/-Django%20REST%20framework-ff9900?style=flat&logo=django&logoColor=white)
![Postman](https://img.shields.io/badge/-Postman-FF6C37?style=flat&logo=postman&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat&logo=docker&logoColor=white)

Foodgram - это онлайн-сервис для создания, поиска и сохранения рецептов. Здесь вы можете найти разнообразные блюда, добавить их в избранное, а также поделиться своими кулинарными шедеврами с другими пользователями.


## Установка и запуск проекта

Для запуска проекта на вашем локальном компьютере выполните следующие шаги:

1. Клонируйте репозиторий на локальную машину:

    ```
    git clone git@github.com:Dxndigiden/foodgram-project-react.git
    ```

2. Перейдите в папку проекта:

    ```
    cd foodgram
    ```

3. Установите зависимости из файла requirements.txt:

    ```
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
    python manage.py runserver
    ```


## Описание проекта

Foodgram - это платформа для обмена рецептами и ингредиентами. Основные функции проекта включают в себя:

- Поиск и просмотр рецептов различных блюд.
- Возможность добавления рецептов в избранное.
- Создание собственных рецептов с указанием ингредиентов и тегов.
- Возможность подписки на других пользователей и просмотра их рецептов.

## Инструкция по развертыванию

1. Установите Docker и Docker Compose на вашем компьютере.
2. Склонируйте репозиторий на вашу локальную машину:

    ```
    git clone git@github.com:Dxndigiden/foodgram-project-react.git
    ```

3. Перейдите в папку проекта:

    ```
    cd foodgram
    ```

4. Создайте файл .env и заполните его данными, указанными в примере ниже.
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
    ```


## Пример .env файла

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_database_name
POSTGRES_USER=your_postgres_username
POSTGRES_PASSWORD=your_postgres_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_django_secret_key
DEBUG=False
```

## Ссылки

- [Развернутый проект](https://foodgrambydxn.sytes.net)

## Автор

Автор: [Dxndigiden](https://github.com/dxndigiden)

