# Команда для полной очистки базы данных.
# Удаляет все записи из всех таблиц, кроме суперпользователя.
#
# Запуск:
#   python manage.py clear_db
#   python manage.py clear_db --yes   (без подтверждения)

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dogs.models import (
    Role, Employee,
    DogStatus, DogSpecialization, TrainingSkill,
    EventType, EquipmentType, VeterinaryProcedureType,
    ServiceDog, DogSpecializationLink,
    Training, ServiceEvent, Equipment,
    VeterinaryRecord, ReportTemplate,
)


class Command(BaseCommand):
    help = 'Полностью очищает базу данных (кроме суперпользователей)'

    def add_arguments(self, parser):
        # Флаг --yes позволяет пропустить запрос подтверждения
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Не спрашивать подтверждение, сразу очистить',
        )

    def handle(self, *args, **options):

        # Запрашиваем подтверждение если флаг --yes не передан
        if not options['yes']:
            self.stdout.write(self.style.WARNING(
                '\n⚠️  ВНИМАНИЕ! Все данные будут безвозвратно удалены!\n'
            ))
            confirm = input('Введите "да" для подтверждения: ')
            if confirm.strip().lower() != 'да':
                self.stdout.write(self.style.NOTICE('Операция отменена.'))
                return

        self.stdout.write('Начинаю очистку базы данных...')

        # Порядок удаления важен: сначала удаляем зависимые записи,
        # потом основные сущности, потом справочники.
        # Иначе PostgreSQL выдаст ошибку нарушения внешнего ключа.

        # 1. Зависимые записи
        count = VeterinaryRecord.objects.all().delete()[0]
        self.stdout.write(f'  Удалено ветеринарных записей: {count}')

        count = Training.objects.all().delete()[0]
        self.stdout.write(f'  Удалено тренировок: {count}')

        count = ServiceEvent.objects.all().delete()[0]
        self.stdout.write(f'  Удалено мероприятий: {count}')

        count = Equipment.objects.all().delete()[0]
        self.stdout.write(f'  Удалено записей снаряжения: {count}')

        count = DogSpecializationLink.objects.all().delete()[0]
        self.stdout.write(f'  Удалено специализаций собак: {count}')

        # 2. Основные сущности
        count = ServiceDog.objects.all().delete()[0]
        self.stdout.write(f'  Удалено служебных собак: {count}')

        count = ReportTemplate.objects.all().delete()[0]
        self.stdout.write(f'  Удалено шаблонов отчётов: {count}')

        # 3. Сотрудники и пользователи (кроме суперпользователей)
        count = Employee.objects.all().delete()[0]
        self.stdout.write(f'  Удалено сотрудников: {count}')

        # Удаляем обычных пользователей, суперпользователей не трогаем
        count = User.objects.filter(is_superuser=False).delete()[0]
        self.stdout.write(f'  Удалено учётных записей: {count}')

        # 4. Справочники
        count = Role.objects.all().delete()[0]
        self.stdout.write(f'  Удалено ролей: {count}')

        count = DogStatus.objects.all().delete()[0]
        self.stdout.write(f'  Удалено статусов собак: {count}')

        count = DogSpecialization.objects.all().delete()[0]
        self.stdout.write(f'  Удалено специализаций: {count}')

        count = TrainingSkill.objects.all().delete()[0]
        self.stdout.write(f'  Удалено навыков тренировок: {count}')

        count = EventType.objects.all().delete()[0]
        self.stdout.write(f'  Удалено типов мероприятий: {count}')

        count = EquipmentType.objects.all().delete()[0]
        self.stdout.write(f'  Удалено типов снаряжения: {count}')

        count = VeterinaryProcedureType.objects.all().delete()[0]
        self.stdout.write(f'  Удалено типов процедур: {count}')

        self.stdout.write(self.style.SUCCESS(
            '\n✅ База данных успешно очищена!'
        ))