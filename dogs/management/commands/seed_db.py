# Команда для заполнения базы данных реалистичными тестовыми данными.
# Создаёт справочники, сотрудников с учётными записями, собак,
# тренировки, мероприятия, ветеринарные записи и снаряжение.
#
# Запуск:
#   python manage.py seed_db

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta, datetime
import random

from dogs.models import (
    Role, Employee,
    DogStatus, DogSpecialization, TrainingSkill,
    EventType, EquipmentType, VeterinaryProcedureType,
    ServiceDog, DogSpecializationLink,
    Training, ServiceEvent, Equipment,
    VeterinaryRecord, ReportTemplate,
)


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю заполнение базы данных...\n')

        # Запускаем каждый блок по порядку
        roles        = self._create_roles()
        statuses     = self._create_statuses()
        specs        = self._create_specializations()
        skills       = self._create_skills()
        event_types  = self._create_event_types()
        equip_types  = self._create_equipment_types()
        proc_types   = self._create_procedure_types()
        employees    = self._create_employees(roles)
        dogs         = self._create_dogs(statuses, employees, specs)
        self._create_trainings(dogs, employees, skills)
        self._create_events(dogs, employees, event_types)
        self._create_vet_records(dogs, employees, proc_types)
        self._create_equipment(dogs, equip_types)
        self._create_report_templates()

        self.stdout.write(self.style.SUCCESS('\n✅ База данных успешно заполнена!'))
        self.stdout.write('\nУчётные записи сотрудников:')
        self.stdout.write('  Руководитель : login=ivanov_chief  | password=Pass1234!')
        self.stdout.write('  Кинолог 1    : login=petrov_k      | password=Pass1234!')
        self.stdout.write('  Кинолог 2    : login=sidorov_k     | password=Pass1234!')
        self.stdout.write('  Кинолог 3    : login=kozlov_k      | password=Pass1234!')
        self.stdout.write('  Ветеринар    : login=smirnova_v    | password=Pass1234!')

    # ==========================================================================
    # СПРАВОЧНИКИ
    # ==========================================================================

    def _create_roles(self):
        self.stdout.write('Создаю роли...')
        roles = {}
        for name in ['Кинолог', 'Ветеринар', 'Руководитель']:
            role, _ = Role.objects.get_or_create(name=name)
            roles[name] = role
        self.stdout.write(f'  Создано ролей: {len(roles)}')
        return roles

    def _create_statuses(self):
        self.stdout.write('Создаю статусы собак...')
        data = [
            'В работе',
            'На лечении',
            'В резерве',
            'На карантине',
            'Списана',
        ]
        statuses = {}
        for name in data:
            obj, _ = DogStatus.objects.get_or_create(name=name, defaults={'is_active': True})
            statuses[name] = obj
        self.stdout.write(f'  Создано статусов: {len(statuses)}')
        return statuses

    def _create_specializations(self):
        self.stdout.write('Создаю специализации...')
        data = [
            'Розыскная',
            'Поиск взрывчатых веществ',
            'Поиск наркотиков',
            'Патрульно-постовая',
            'Охрана объектов',
            'Конвойная',
        ]
        specs = {}
        for name in data:
            obj, _ = DogSpecialization.objects.get_or_create(name=name, defaults={'is_active': True})
            specs[name] = obj
        self.stdout.write(f'  Создано специализаций: {len(specs)}')
        return specs

    def _create_skills(self):
        self.stdout.write('Создаю навыки тренировок...')
        data = [
            'Послушание',
            'Поиск по следу',
            'Задержание',
            'Обыск местности',
            'Поиск взрывчатых веществ',
            'Поиск наркотических веществ',
            'Охрана хозяина',
            'Преодоление препятствий',
        ]
        skills = {}
        for name in data:
            obj, _ = TrainingSkill.objects.get_or_create(name=name, defaults={'is_active': True})
            skills[name] = obj
        self.stdout.write(f'  Создано навыков: {len(skills)}')
        return skills

    def _create_event_types(self):
        self.stdout.write('Создаю типы мероприятий...')
        data = [
            'Охрана общественного порядка',
            'Осмотр объекта',
            'Поиск взрывчатых веществ',
            'Поиск по следу',
            'Патрулирование территории',
            'Сопровождение конвоя',
        ]
        types = {}
        for name in data:
            obj, _ = EventType.objects.get_or_create(name=name, defaults={'is_active': True})
            types[name] = obj
        self.stdout.write(f'  Создано типов мероприятий: {len(types)}')
        return types

    def _create_equipment_types(self):
        self.stdout.write('Создаю типы снаряжения...')
        data = [
            'Ошейник',
            'Поводок',
            'Намордник',
            'Шлейка',
            'Нагрудник защитный',
            'Контейнер транспортировочный',
        ]
        types = {}
        for name in data:
            obj, _ = EquipmentType.objects.get_or_create(name=name, defaults={'is_active': True})
            types[name] = obj
        self.stdout.write(f'  Создано типов снаряжения: {len(types)}')
        return types

    def _create_procedure_types(self):
        self.stdout.write('Создаю типы ветеринарных процедур...')
        data = [
            'Вакцинация',
            'Обработка от паразитов',
            'Плановый осмотр',
            'Лечение',
            'Чипирование',
            'Стоматологический осмотр',
        ]
        types = {}
        for name in data:
            obj, _ = VeterinaryProcedureType.objects.get_or_create(name=name, defaults={'is_active': True})
            types[name] = obj
        self.stdout.write(f'  Создано типов процедур: {len(types)}')
        return types

    # ==========================================================================
    # СОТРУДНИКИ
    # ==========================================================================

    def _create_employees(self, roles):
        self.stdout.write('Создаю сотрудников...')

        # Данные сотрудников: (логин, пароль, ФИО, звание, должность, роль, отдел, найм, аттестация)
        employees_data = [
            {
                'username': 'ivanov_chief',
                'first_name': 'Александр',
                'last_name': 'Иванов',
                'full_name': 'Иванов Александр Сергеевич',
                'rank': 'Подполковник полиции',
                'position': 'Начальник Центра кинологической службы',
                'role': 'Руководитель',
                'department': 'Центр кинологической службы',
                'phone': '+7 (846) 221-01-01',
                'hire_date': date(2015, 3, 1),
                'cert_date': date(2023, 3, 1),
            },
            {
                'username': 'petrov_k',
                'first_name': 'Дмитрий',
                'last_name': 'Петров',
                'full_name': 'Петров Дмитрий Александрович',
                'rank': 'Старший сержант полиции',
                'position': 'Инструктор-кинолог',
                'role': 'Кинолог',
                'department': 'Отдел кинологической службы №1',
                'phone': '+7 (846) 221-01-02',
                'hire_date': date(2018, 6, 15),
                'cert_date': date(2022, 6, 15),
            },
            {
                'username': 'sidorov_k',
                'first_name': 'Николай',
                'last_name': 'Сидоров',
                'full_name': 'Сидоров Николай Викторович',
                'rank': 'Сержант полиции',
                'position': 'Кинолог',
                'role': 'Кинолог',
                'department': 'Отдел кинологической службы №1',
                'phone': '+7 (846) 221-01-03',
                'hire_date': date(2020, 9, 1),
                'cert_date': date(2022, 9, 1),
            },
            {
                'username': 'kozlov_k',
                'first_name': 'Андрей',
                'last_name': 'Козлов',
                'full_name': 'Козлов Андрей Игоревич',
                'rank': 'Младший сержант полиции',
                'position': 'Кинолог',
                'role': 'Кинолог',
                'department': 'Отдел кинологической службы №2',
                'phone': '+7 (846) 221-01-04',
                'hire_date': date(2021, 4, 20),
                'cert_date': date(2023, 4, 20),
            },
            {
                'username': 'smirnova_v',
                'first_name': 'Елена',
                'last_name': 'Смирнова',
                'full_name': 'Смирнова Елена Павловна',
                'rank': 'Капитан полиции',
                'position': 'Ветеринарный врач',
                'role': 'Ветеринар',
                'department': 'Ветеринарная служба',
                'phone': '+7 (846) 221-01-05',
                'hire_date': date(2017, 1, 10),
                'cert_date': date(2021, 1, 10),
            },
        ]

        employees = []
        for data in employees_data:
            # Создаём или получаем учётную запись Django
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_staff': False,
                }
            )
            if created:
                user.set_password('Pass1234!')
                user.save()

            # Создаём или получаем карточку сотрудника
            emp, _ = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': data['full_name'],
                    'rank': data['rank'],
                    'position': data['position'],
                    'department': data['department'],
                    'phone': data['phone'],
                    'hire_date': data['hire_date'],
                    'certification_date': data['cert_date'],
                    'is_active': True,
                }
            )

            # Назначаем роль
            emp.roles.add(roles[data['role']])
            employees.append(emp)

        self.stdout.write(f'  Создано сотрудников: {len(employees)}')
        return employees

    # ==========================================================================
    # СЛУЖЕБНЫЕ СОБАКИ
    # ==========================================================================

    def _create_dogs(self, statuses, employees, specs):
        self.stdout.write('Создаю служебных собак...')

        # Кинологи — сотрудники с ролью Кинолог
        kennel_officers = [e for e in employees if e.roles.filter(name='Кинолог').exists()]

        dogs_data = [
            {
                'name': 'Граф',
                'inventory_number': 'КС-2019-001',
                'breed': 'Немецкая овчарка',
                'gender': 'Кобель',
                'birth_date': date(2019, 4, 12),
                'arrival_date': date(2020, 1, 15),
                'status': 'В работе',
                'kennel_idx': 0,
                'specs': ['Розыскная', 'Поиск наркотиков'],
                'origin': 'Получен из питомника МВД России г. Москва',
            },
            {
                'name': 'Рекс',
                'inventory_number': 'КС-2018-002',
                'breed': 'Бельгийская малинуа',
                'gender': 'Кобель',
                'birth_date': date(2018, 7, 3),
                'arrival_date': date(2019, 3, 20),
                'status': 'В работе',
                'kennel_idx': 0,
                'specs': ['Поиск взрывчатых веществ'],
                'origin': 'Приобретён по государственному контракту',
            },
            {
                'name': 'Альфа',
                'inventory_number': 'КС-2020-003',
                'breed': 'Немецкая овчарка',
                'gender': 'Сука',
                'birth_date': date(2020, 2, 28),
                'arrival_date': date(2021, 5, 10),
                'status': 'В работе',
                'kennel_idx': 1,
                'specs': ['Патрульно-постовая', 'Задержание'],
                'origin': 'Получена из питомника МВД России г. Самара',
            },
            {
                'name': 'Буран',
                'inventory_number': 'КС-2017-004',
                'breed': 'Лабрадор ретривер',
                'gender': 'Кобель',
                'birth_date': date(2017, 11, 5),
                'arrival_date': date(2018, 8, 1),
                'status': 'На лечении',
                'kennel_idx': 1,
                'specs': ['Поиск наркотиков'],
                'origin': 'Получен из питомника ФСБ России',
            },
            {
                'name': 'Дина',
                'inventory_number': 'КС-2021-005',
                'breed': 'Немецкая овчарка',
                'gender': 'Сука',
                'birth_date': date(2021, 6, 17),
                'arrival_date': date(2022, 9, 5),
                'status': 'В работе',
                'kennel_idx': 2,
                'specs': ['Розыскная'],
                'origin': 'Приобретена по государственному контракту',
            },
            {
                'name': 'Зевс',
                'inventory_number': 'КС-2016-006',
                'breed': 'Ротвейлер',
                'gender': 'Кобель',
                'birth_date': date(2016, 3, 22),
                'arrival_date': date(2017, 5, 18),
                'status': 'В резерве',
                'kennel_idx': 2,
                'specs': ['Патрульно-постовая', 'Охрана объектов'],
                'origin': 'Передан из МВД Оренбургской области',
            },
            {
                'name': 'Ирма',
                'inventory_number': 'КС-2022-007',
                'breed': 'Спрингер-спаниель',
                'gender': 'Сука',
                'birth_date': date(2022, 1, 9),
                'arrival_date': date(2023, 3, 14),
                'status': 'В работе',
                'kennel_idx': 0,
                'specs': ['Поиск взрывчатых веществ', 'Поиск наркотиков'],
                'origin': 'Получена из питомника МВД России г. Москва',
            },
            {
                'name': 'Торос',
                'inventory_number': 'КС-2015-008',
                'breed': 'Немецкая овчарка',
                'gender': 'Кобель',
                'birth_date': date(2015, 8, 30),
                'arrival_date': date(2016, 10, 5),
                'status': 'Списана',
                'kennel_idx': 1,
                'specs': ['Розыскная', 'Конвойная'],
                'origin': 'Получен из питомника МВД России г. Самара',
            },
        ]

        dogs = []
        for data in dogs_data:
            kennel = kennel_officers[data['kennel_idx'] % len(kennel_officers)]
            dog, created = ServiceDog.objects.get_or_create(
                inventory_number=data['inventory_number'],
                defaults={
                    'name': data['name'],
                    'breed': data['breed'],
                    'gender': data['gender'],
                    'birth_date': data['birth_date'],
                    'arrival_date': data['arrival_date'],
                    'status': statuses[data['status']],
                    'main_kennel': kennel,
                    'color_marks': 'Стандартный окрас породы, особых примет нет',
                    'origin_story': data['origin'],
                }
            )
            if created:
                # Назначаем специализации
                for i, spec_name in enumerate(data['specs']):
                    if spec_name in specs:
                        DogSpecializationLink.objects.get_or_create(
                            dog=dog,
                            specialization=specs[spec_name],
                            defaults={
                                'assignment_date': data['arrival_date'] + timedelta(days=90 * (i + 1))
                            }
                        )
            dogs.append(dog)

        self.stdout.write(f'  Создано собак: {len(dogs)}')
        return dogs

    # ==========================================================================
    # ТРЕНИРОВКИ
    # ==========================================================================

    def _create_trainings(self, dogs, employees, skills):
        self.stdout.write('Создаю тренировки...')

        kennel_officers = [e for e in employees if e.roles.filter(name='Кинолог').exists()]
        skills_list = list(skills.values())
        weather_options = [
            'Ясно, +18°C', 'Облачно, +12°C', 'Ясно, +25°C',
            'Пасмурно, +8°C', 'Дождь, +10°C', 'Ясно, -5°C, снег',
        ]
        count = 0

        # Для каждой активной собаки создаём 8 тренировок за последние 3 месяца
        active_dogs = [d for d in dogs if d.status.name != 'Списана']
        for dog in active_dogs:
            kennel = dog.main_kennel or random.choice(kennel_officers)
            for i in range(8):
                days_ago = random.randint(1, 90)
                dt = timezone.now() - timedelta(days=days_ago)
                Training.objects.get_or_create(
                    dog=dog,
                    datetime=dt,
                    defaults={
                        'kennel': kennel,
                        'skill': random.choice(skills_list),
                        'duration': timedelta(hours=1, minutes=random.choice([0, 30])),
                        'weather_conditions': random.choice(weather_options),
                        'score': random.randint(3, 5),
                        'comments': random.choice([
                            'Собака работала уверенно, замечаний нет.',
                            'Небольшие затруднения при отработке навыка.',
                            'Отличный результат, норматив выполнен.',
                            'Требуется дополнительная отработка.',
                            '',
                        ]),
                    }
                )
                count += 1

        self.stdout.write(f'  Создано тренировок: {count}')

    # ==========================================================================
    # СЛУЖЕБНЫЕ МЕРОПРИЯТИЯ
    # ==========================================================================

    def _create_events(self, dogs, employees, event_types):
        self.stdout.write('Создаю служебные мероприятия...')

        kennel_officers = [e for e in employees if e.roles.filter(name='Кинолог').exists()]
        types_list = list(event_types.values())
        locations = [
            'ул. Ленина, д. 45, г. Самара',
            'Железнодорожный вокзал, г. Самара',
            'ТЦ "Мегa", г. Самара',
            'Стадион "Солидарность Самара Арена"',
            'Площадь Куйбышева, г. Самара',
            'Аэропорт Курумоч, г. Самара',
            'ул. Победы, д. 100, г. Тольятти',
            'Административный центр, г. Сызрань',
        ]
        count = 0

        active_dogs = [d for d in dogs if d.status.name not in ('Списана', 'В резерве')]
        for dog in active_dogs:
            kennel = dog.main_kennel or random.choice(kennel_officers)
            for i in range(4):
                days_ago = random.randint(1, 180)
                dt = timezone.now() - timedelta(days=days_ago)
                ServiceEvent.objects.get_or_create(
                    dog=dog,
                    datetime=dt,
                    defaults={
                        'kennel': kennel,
                        'event_type': random.choice(types_list),
                        'location': random.choice(locations),
                        'duration': timedelta(hours=random.randint(2, 6)),
                        'results': random.choice([
                            'Нарушений не выявлено, обстановка спокойная.',
                            'Собака сработала положительно, обнаружен посторонний запах.',
                            'Мероприятие завершено в штатном режиме.',
                            'Проведён полный осмотр объекта, замечаний нет.',
                        ]),
                    }
                )
                count += 1

        self.stdout.write(f'  Создано мероприятий: {count}')

    # ==========================================================================
    # ВЕТЕРИНАРНЫЕ ЗАПИСИ
    # ==========================================================================

    def _create_vet_records(self, dogs, employees, proc_types):
        self.stdout.write('Создаю ветеринарные записи...')

        vets = [e for e in employees if e.roles.filter(name='Ветеринар').exists()]
        if not vets:
            vets = employees
        vet = vets[0]

        types_list = list(proc_types.values())
        count = 0

        for dog in dogs:
            # Плановые процедуры за последний год
            for i in range(3):
                proc_date = date.today() - timedelta(days=random.randint(30, 365))
                next_date = proc_date + timedelta(days=180)
                VeterinaryRecord.objects.get_or_create(
                    dog=dog,
                    procedure_date=proc_date,
                    defaults={
                        'veterinarian': vet,
                        'procedure_type': random.choice(types_list),
                        'description': 'Плановая процедура проведена в полном объёме. Отклонений не выявлено.',
                        'next_procedure_date': next_date if i == 0 else None,
                        'is_routine': True,
                        'notes': '',
                    }
                )
                count += 1

            # Для собаки "На лечении" добавляем внеплановую запись
            if dog.status.name == 'На лечении':
                VeterinaryRecord.objects.get_or_create(
                    dog=dog,
                    procedure_date=date.today() - timedelta(days=5),
                    defaults={
                        'veterinarian': vet,
                        'procedure_type': proc_types.get('Лечение', types_list[0]),
                        'description': 'Внеплановый осмотр. Назначено лечение, курс 10 дней.',
                        'next_procedure_date': date.today() + timedelta(days=10),
                        'is_routine': False,
                        'notes': 'Динамика положительная, состояние стабильное.',
                    }
                )
                count += 1

        self.stdout.write(f'  Создано ветеринарных записей: {count}')

    # ==========================================================================
    # СНАРЯЖЕНИЕ
    # ==========================================================================

    def _create_equipment(self, dogs, equip_types):
        self.stdout.write('Создаю записи снаряжения...')

        # Базовый набор снаряжения для каждой собаки
        base_equipment = ['Ошейник', 'Поводок', 'Намордник']
        conditions = ['Хорошее', 'Удовлетворительное', 'Новое']
        count = 0

        for dog in dogs:
            if dog.status.name == 'Списана':
                continue
            for eq_name in base_equipment:
                if eq_name in equip_types:
                    Equipment.objects.get_or_create(
                        dog=dog,
                        equipment_type=equip_types[eq_name],
                        defaults={
                            'issue_date': dog.arrival_date + timedelta(days=7),
                            'current_condition': random.choice(conditions),
                            'notes': '',
                        }
                    )
                    count += 1

        self.stdout.write(f'  Создано записей снаряжения: {count}')

    # ==========================================================================
    # ШАБЛОНЫ ОТЧЁТОВ
    # ==========================================================================

    def _create_report_templates(self):
        self.stdout.write('Создаю шаблоны отчётов...')
        templates = [
            ('Список служебных собак', 'dogs'),
            ('Журнал тренировочных занятий', 'trainings'),
            ('Ветеринарные мероприятия', 'vet'),
            ('Служебные мероприятия', 'events'),
        ]
        for name, rtype in templates:
            ReportTemplate.objects.get_or_create(
                name=name,
                defaults={
                    'report_type': rtype,
                    'template_file': '',
                }
            )
        self.stdout.write(f'  Создано шаблонов: {len(templates)}')