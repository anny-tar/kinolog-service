# Команда для быстрого создания суперпользователя с заранее заданными данными.
# Удобно при первом развёртывании системы или после полного сброса БД.
#
# Запуск:
#   python manage.py create_superuser_default
#
# Данные по умолчанию:
#   Логин   : admin
#   Пароль  : Admin1234!
#   Email   : admin@mvd.local
#
# Можно переопределить через аргументы:
#   python manage.py create_superuser_default --username boss --password Secret99!

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Создаёт суперпользователя с заранее заданными логином и паролем'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Логин суперпользователя (по умолчанию: admin)',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Admin1234!',
            help='Пароль суперпользователя (по умолчанию: Admin1234!)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@mvd.local',
            help='Email суперпользователя (по умолчанию: admin@mvd.local)',
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email    = options['email']

        # Проверяем — вдруг такой пользователь уже существует
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f'⚠️  Пользователь «{username}» уже существует. Обновляю пароль...'
            ))
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.email = email
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'✅ Пароль пользователя «{username}» обновлён.'
            ))
        else:
            # Создаём нового суперпользователя
            User.objects.create_superuser(
                username=username,
                password=password,
                email=email,
            )
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Суперпользователь успешно создан!\n'
            ))

        # Выводим итоговые данные для входа
        self.stdout.write('Данные для входа:')
        self.stdout.write(f'  Адрес админки : http://127.0.0.1:8000/admin/')
        self.stdout.write(f'  Логин         : {username}')
        self.stdout.write(f'  Пароль        : {password}')