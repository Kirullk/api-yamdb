# 🎬 YaMDb API

## 📖 О проекте

**YaMDb** — это бэкенд-приложение для сбора отзывов пользователей на различные произведения (книги, фильмы, музыка).

Сами произведения делятся на **категории** и **жанры**. Пользователи могут оставлять **текстовые отзывы** и выставлять **оценки от 1 до 10**, на основе которых автоматически рассчитывается **средний рейтинг** произведения. Также к отзывам можно добавлять **комментарии**.

Проект построен на **Django REST Framework** с использованием **JWT-аутентификации**, ролевой модели доступа и полной документации в формате **ReDoc**.

---

## 🚀 Быстрый старт

### Клонирование репозитория

```bash
git clone https://github.com/Kirullk/api-yamdb.git
cd api-yamdb
```

### Настройка окружения

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Миграции и запуск

```bash
python manage.py migrate
python manage.py runserver
```

### Доступ к документации API

После запуска сервера документация доступна по адресу:  
👉 **[http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)**

---

## 🛠 Технологии

| Компонент | Технология |
|-----------|------------|
| Бэкенд | Django 3.2+ |
| API | Django REST Framework 3.12+ |
| Аутентификация | JWT (SimpleJWT) |
| База данных | SQLite (разработка) / PostgreSQL (продакшн) |
| Документация | ReDoc (OpenAPI) |
| Фильтрация | Django Filter |
| Почта | Django Email (консольный бэкенд) |

---

## 📌 Основные возможности

- ✅ Регистрация пользователей с подтверждением по email
- ✅ JWT-аутентификация
- ✅ Ролевая модель: `user`, `moderator`, `admin`
- ✅ CRUD для категорий, жанров и произведений
- ✅ Отзывы и оценки (1–10)
- ✅ Комментарии к отзывам
- ✅ Рейтинг произведений (средняя оценка)
- ✅ Фильтрация, поиск и пагинация
- ✅ Документация API (ReDoc)

---

## 🔐 Роли и права доступа

| Роль | Права |
|------|-------|
| **Аноним** | Просмотр описаний произведений, отзывов и комментариев |
| **Аутентифицированный пользователь** (`user`) | Чтение всего + публикация отзывов и комментариев, редактирование/удаление своих отзывов и комментариев |
| **Модератор** (`moderator`) | Все права `user` + удаление любых отзывов и комментариев |
| **Администратор** (`admin`) | Полный доступ ко всему контенту + управление пользователями |
| **Суперпользователь Django** | Все права администратора |

---

## 🧩 API Эндпоинты

Все запросы начинаются с `/api/v1/`.

### 🔑 Аутентификация

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/auth/signup/` | Регистрация нового пользователя (отправка кода на email) |
| `POST` | `/auth/token/` | Получение JWT-токена по коду подтверждения |

### 👤 Пользователи

| Метод | Эндпоинт | Доступ | Описание |
|-------|----------|--------|----------|
| `GET` | `/users/` | admin | Список всех пользователей |
| `POST` | `/users/` | admin | Создание пользователя |
| `GET` | `/users/{username}/` | admin | Получение пользователя |
| `PATCH` | `/users/{username}/` | admin | Изменение пользователя |
| `DELETE` | `/users/{username}/` | admin | Удаление пользователя |
| `GET` | `/users/me/` | auth | Получение своего профиля |
| `PATCH` | `/users/me/` | auth | Изменение своего профиля |

### 📚 Категории, жанры, произведения

| Метод | Эндпоинт | Доступ | Описание |
|-------|----------|--------|----------|
| `GET` | `/categories/` | all | Список категорий |
| `POST` | `/categories/` | admin | Создание категории |
| `DELETE` | `/categories/{slug}/` | admin | Удаление категории |
| `GET` | `/genres/` | all | Список жанров |
| `POST` | `/genres/` | admin | Создание жанра |
| `DELETE` | `/genres/{slug}/` | admin | Удаление жанра |
| `GET` | `/titles/` | all | Список произведений |
| `POST` | `/titles/` | admin | Создание произведения |
| `GET` | `/titles/{id}/` | all | Детали произведения |
| `PATCH` | `/titles/{id}/` | admin | Обновление произведения |
| `DELETE` | `/titles/{id}/` | admin | Удаление произведения |

### 💬 Отзывы и комментарии

| Метод | Эндпоинт | Доступ | Описание |
|-------|----------|--------|----------|
| `GET` | `/titles/{title_id}/reviews/` | all | Список отзывов |
| `POST` | `/titles/{title_id}/reviews/` | auth | Добавление отзыва |
| `GET` | `/titles/{title_id}/reviews/{review_id}/` | all | Детали отзыва |
| `PATCH` | `/titles/{title_id}/reviews/{review_id}/` | author/moderator/admin | Обновление отзыва |
| `DELETE` | `/titles/{title_id}/reviews/{review_id}/` | author/moderator/admin | Удаление отзыва |
| `GET` | `/titles/{title_id}/reviews/{review_id}/comments/` | all | Список комментариев |
| `POST` | `/titles/{title_id}/reviews/{review_id}/comments/` | auth | Добавление комментария |
| `GET` | `/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` | all | Детали комментария |
| `PATCH` | `/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` | author/moderator/admin | Обновление комментария |
| `DELETE` | `/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` | author/moderator/admin | Удаление комментария |

---

## 📝 Примеры запросов

### 1. Регистрация пользователя

```http
POST /api/v1/auth/signup/
Content-Type: application/json

{
    "username": "kirill",
    "email": "kirill@example.com"
}
```

**Ответ:**
```json
{
    "email": "kirill@example.com",
    "username": "kirill"
}
```

### 2. Получение JWT-токена

```http
POST /api/v1/auth/token/
Content-Type: application/json

{
    "username": "kirill",
    "confirmation_code": "123456"
}
```

**Ответ:**
```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 3. Добавление отзыва (с токеном)

```http
POST /api/v1/titles/1/reviews/
Authorization: Bearer <token>
Content-Type: application/json

{
    "text": "Отличный фильм!",
    "score": 9
}
```

**Ответ:**
```json
{
    "id": 1,
    "text": "Отличный фильм!",
    "author": "kirill",
    "score": 9,
    "pub_date": "2025-04-07T12:00:00Z"
}
```

### 4. Получение списка произведений с фильтрацией

```http
GET /api/v1/titles/?genre=comedy&year=1999
```

**Ответ:**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [...]
}
```

---

## 📄 Документация

Полная документация API доступна в формате **ReDoc**:

🔗 [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

---

## 🤝 Команда разработчиков

| Роль | Имя | Telegram |
|------|-----|----------|
| **Первый разработчик** | Кирилл Шишлов | [@kiyrer](https://t.me/kiyrer) |
| **Второй разработчик** | Вячеслав Пак | [@silentway2](https://t.me/silentway2) |
| **Третий разработчик** | Роман Калининченко | [@sqwhh](https://t.me/sqwhh) |

---

**✨ Удачи в использовании YaMDb!**
