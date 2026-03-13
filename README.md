# 🐕 Кинологическая служба МВД — Веб-сервис

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-green?logo=django)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue?logo=postgresql)](https://postgresql.org)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)](https://getbootstrap.com)

Веб-сервис для автоматизации учётной и отчётной деятельности  
**Центра кинологической службы ГУ МВД России по Самарской области**.


---

## 📋 О проекте

Система заменяет бумажные журналы и таблицы Excel единой цифровой платформой.  
Охватывает все ключевые направления работы подразделения:

- 🐾 Учёт служебных собак, их специализаций и снаряжения
- 🏋️ Журнал тренировочных занятий
- 🚔 Учёт служебных мероприятий
- 💉 Ветеринарное сопровождение
- 👥 Управление персоналом
- 📄 Автоматическая генерация отчётов в формате `.docx`

---

## 🛠️ Технологический стек

| Компонент | Технология |
|---|---|
| Бэкенд | Python 3, Django 4 |
| База данных | PostgreSQL 13+ |
| Фронтенд | HTML5, CSS3, JavaScript, Bootstrap 5 |
| Отчётность | python-docx |
| Работа с изображениями | Pillow |
| Очистка файлов | django-cleanup |

---

## 👥 Роли пользователей

| Роль | Доступ |
|---|---|
| **Администратор** | Полный доступ, управление пользователями и справочниками |
| **Руководитель** | Просмотр всех данных, формирование отчётов |
| **Кинолог** | Учёт собак, тренировок и мероприятий |
| **Ветеринар** | Ветеринарные записи, просмотр карточек собак |

---

## 🚀 Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/anny-tar/kinolog-service.git
cd kinolog-service
```

### 2. Создать и активировать виртуальное окружение

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Настроить базу данных

Создать базу данных PostgreSQL:

```sql
CREATE DATABASE kinolog_db;
```

Создать файл `.env` в корне проекта (на основе `.env.example`):

```env
SECRET_KEY=ваш_секретный_ключ
DB_NAME=kinolog_db
DB_USER=postgres
DB_PASSWORD=ваш_пароль
DB_HOST=localhost
DB_PORT=5432
```

### 5. Применить миграции

```bash
python manage.py migrate
```

### 6. Создать суперпользователя

```bash
# Быстрый способ (логин: admin, пароль: Admin1234!)
python manage.py create_superuser_default

# Или стандартный способ Django
python manage.py createsuperuser
```

### 7. Заполнить базу тестовыми данными (опционально)

```bash
python manage.py seed_db
```

### 8. Запустить сервер

```bash
python manage.py runserver
```

Открыть в браузере: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Админ-панель: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## ⚙️ Управляющие команды

```bash
# Заполнить БД тестовыми данными
python manage.py seed_db

# Полностью очистить БД
python manage.py clear_db

# Создать резервную копию БД
python manage.py backup_db

# Создать резервную копию в указанную папку
python manage.py backup_db --output C:/backups

# Создать суперпользователя с параметрами по умолчанию
python manage.py create_superuser_default
```

---

## 📁 Структура проекта

```
kinolog_service/
├── config/                  # Настройки проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dogs/                    # Основное приложение
│   ├── management/
│   │   └── commands/        # Управляющие команды
│   │       ├── seed_db.py
│   │       ├── clear_db.py
│   │       ├── backup_db.py
│   │       └── create_superuser_default.py
│   ├── templatetags/        # Кастомные теги шаблонов
│   ├── models.py            # Модели данных (15 сущностей)
│   ├── views.py             # Логика представлений
│   ├── forms.py             # Формы
│   ├── admin.py             # Настройка админ-панели
│   ├── decorators.py        # Проверка ролей
│   ├── context_processors.py
│   └── report_generator.py  # Генерация отчётов .docx
├── templates/               # HTML-шаблоны
│   ├── base.html
│   ├── login.html
│   └── dogs/
├── static/                  # CSS и JavaScript
│   ├── css/
│   └── js/
├── media/                   # Загружаемые файлы (не в git)
├── backups/                 # Резервные копии БД (не в git)
├── requirements.txt
├── .gitignore
└── manage.py
```

---

## 📊 Структура базы данных

Система содержит 15 моделей данных, объединённых в три модуля:

**Модуль «Кинолог»:** ServiceDog, DogStatus, DogSpecialization, DogSpecializationLink, Training, TrainingSkill, ServiceEvent, EventType, Equipment, EquipmentType

**Модуль «Ветеринария»:** VeterinaryRecord, VeterinaryProcedureType

**Модуль «Руководитель»:** Employee, Role, ReportTemplate

---

## 📄 Отчёты

Система формирует четыре типа отчётов в формате `.docx`:

| Отчёт | Фильтр по периоду |
|---|---|
| Список служебных собак | — |
| Журнал тренировочных занятий | ✅ |
| Ветеринарные мероприятия | ✅ |
| Служебные мероприятия | ✅ |

