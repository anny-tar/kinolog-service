# Команда для создания резервной копии базы данных PostgreSQL.
# Использует утилиту pg_dump, которая входит в стандартную поставку PostgreSQL.
#
# Запуск:
#   python manage.py backup_db
#   python manage.py backup_db --output C:/backups   (указать папку)

import os
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Создаёт резервную копию базы данных PostgreSQL в файл .sql'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Папка для сохранения резервной копии (по умолчанию: папка backups/ в корне проекта)',
        )

    def handle(self, *args, **options):

        # Читаем настройки подключения из settings.py
        db = settings.DATABASES['default']
        db_name = db.get('NAME', '')
        db_user = db.get('USER', '')
        db_password = db.get('PASSWORD', '')
        db_host = db.get('HOST', 'localhost')
        db_port = db.get('PORT', '5432')

        # Определяем папку для сохранения бэкапа
        if options['output']:
            backup_dir = options['output']
        else:
            # По умолчанию создаём папку backups/ в корне проекта
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')

        # Создаём папку если её нет
        os.makedirs(backup_dir, exist_ok=True)

        # Формируем имя файла с датой и временем
        # Пример: backup_kinolog_db_2026-03-13_14-30-00.sql
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'backup_{db_name}_{timestamp}.sql'
        filepath = os.path.join(backup_dir, filename)

        self.stdout.write(f'Создаю резервную копию базы данных «{db_name}»...')
        self.stdout.write(f'Файл: {filepath}')

        # Передаём пароль через переменную окружения PGPASSWORD —
        # это стандартный способ, безопаснее чем передавать в аргументах командной строки
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password

        # Формируем команду pg_dump
        # -F p  — формат plain SQL (читаемый текстовый файл)
        # -h    — хост
        # -p    — порт
        # -U    — пользователь
        # -f    — выходной файл
        command = [
            'pg_dump',
            '-F', 'p',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-f', filepath,
            db_name,
        ]

        try:
            result = subprocess.run(
                command,
                env=env,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Узнаём размер созданного файла
                size_kb = os.path.getsize(filepath) // 1024
                self.stdout.write(self.style.SUCCESS(
                    f'\n✅ Резервная копия успешно создана!'
                ))
                self.stdout.write(f'   Файл: {filepath}')
                self.stdout.write(f'   Размер: {size_kb} КБ')
            else:
                # pg_dump вернул ошибку
                self.stdout.write(self.style.ERROR(
                    f'\n❌ Ошибка при создании резервной копии:'
                ))
                self.stdout.write(result.stderr)

        except FileNotFoundError:
            # pg_dump не найден в PATH
            self.stdout.write(self.style.ERROR(
                '\n❌ Утилита pg_dump не найдена!\n'
                'Убедитесь что PostgreSQL установлен и папка bin добавлена в PATH.\n'
                'Обычно путь выглядит так: C:\\Program Files\\PostgreSQL\\16\\bin'
            ))