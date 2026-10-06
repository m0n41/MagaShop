# MagaShop

Веб-магазин на Django с отдельным REST API на Django REST Framework. HTML-сайт и API используют общие приложения и модели проекта.

## Возможности

- каталог товаров и категорий;
- корзина и оформление заказов;
- учётные записи и профили пользователей;
- отзывы, избранное и купоны;
- REST API с префиксом `/api/v1/`.

## Технологии

- Python
- Django 5.2
- Django REST Framework
- PostgreSQL

## Требования

- Python версии, совместимой с зависимостями проекта;
- PostgreSQL;
- PowerShell (примеры команд ниже приведены для Windows).

## Установка и запуск

Выполните команды из корневой папки проекта:

```powershell
python -m venv djvenv
.\djvenv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item config\.env.example config\.env
```

Откройте `config\.env` и укажите настройки базы данных и приложения. Django ожидает параметры `SECRET_KEY`, `DB_PASSWORD`, `SOCIAL_AUTH_GITHUB_KEY` и `SOCIAL_AUTH_GITHUB_SECRET`; также можно настроить `DEBUG`, `ALLOWED_HOSTS`, `DB_NAME`, `DB_USER`, `DB_HOST` и `DB_PORT`. Не используйте тестовый `SECRET_KEY` и `DEBUG=True` в production.

Создайте базу данных PostgreSQL, затем примените миграции и запустите сервер:

```powershell
python config\manage.py migrate
python config\manage.py createsuperuser
python config\manage.py runserver
```

Сайт будет доступен по адресу `http://127.0.0.1:8000/`, панель администратора — по адресу `http://127.0.0.1:8000/admin/`, API — по адресу `http://127.0.0.1:8000/api/v1/`.

## Тесты

После установки зависимостей и настройки тестовой базы данных запустите:

```powershell
python config\manage.py test
```

## Конфигурация и безопасность

Локальные настройки хранятся в `config\.env`. Не добавляйте в Git `.env`-файлы, пароли, токены, ключи OAuth, пользовательские загрузки или локальную базу данных. Шаблон переменных окружения находится в `config\.env.example`.
