# dogs/tests.py
#
# Тесты для веб-сервиса кинологической службы.
# Охватывают 4 направления:
#   1. Модели — создание записей и связи между ними
#   2. Авторизация — вход, выход, неверный пароль
#   3. Роли — доступ закрыт для чужих ролей
#   4. Страницы — коды ответов и перенаправления
#
# Запуск всех тестов:
#   python manage.py test dogs
#
# Запуск конкретного класса:
#   python manage.py test dogs.tests.ModelTests
#   python manage.py test dogs.tests.AuthTests
#   python manage.py test dogs.tests.RoleAccessTests
#   python manage.py test dogs.tests.PageTests

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta

from .models import (
    Role, Employee, DogStatus, DogSpecialization,
    TrainingSkill, EventType, EquipmentType,
    VeterinaryProcedureType, ServiceDog,
    DogSpecializationLink, Training, VeterinaryRecord,
)


# ==============================================================================
# ВСПОМОГАТЕЛЬНЫЙ КЛАСС — общие данные для всех тестов
# ==============================================================================

class BaseTestCase(TestCase):
    """
    Базовый класс с готовыми данными.
    Все остальные классы тестов наследуют его,
    чтобы не повторять код создания пользователей и справочников.
    """

    def setUp(self):
        """setUp вызывается автоматически перед каждым тестом"""

        # --- Создаём роли ---
        self.role_kennel  = Role.objects.create(name='Кинолог')
        self.role_vet     = Role.objects.create(name='Ветеринар')
        self.role_manager = Role.objects.create(name='Руководитель')

        # --- Создаём справочники ---
        self.status_active = DogStatus.objects.create(name='В работе', is_active=True)
        self.status_sick   = DogStatus.objects.create(name='На лечении', is_active=True)
        self.spec_search   = DogSpecialization.objects.create(name='Розыскная', is_active=True)
        self.skill         = TrainingSkill.objects.create(name='Послушание', is_active=True)
        self.proc_type     = VeterinaryProcedureType.objects.create(name='Вакцинация', is_active=True)

        # --- Создаём пользователей Django ---
        self.user_kennel  = User.objects.create_user(username='kennel_user',  password='testpass123')
        self.user_vet     = User.objects.create_user(username='vet_user',     password='testpass123')
        self.user_manager = User.objects.create_user(username='manager_user', password='testpass123')

        # --- Создаём сотрудников и привязываем роли ---
        self.emp_kennel = Employee.objects.create(
            user=self.user_kennel,
            full_name='Петров Дмитрий Александрович',
            rank='Сержант полиции',
            position='Кинолог',
            is_active=True,
        )
        self.emp_kennel.roles.add(self.role_kennel)

        self.emp_vet = Employee.objects.create(
            user=self.user_vet,
            full_name='Смирнова Елена Павловна',
            rank='Капитан полиции',
            position='Ветеринар',
            is_active=True,
        )
        self.emp_vet.roles.add(self.role_vet)

        self.emp_manager = Employee.objects.create(
            user=self.user_manager,
            full_name='Иванов Александр Сергеевич',
            rank='Подполковник полиции',
            position='Начальник',
            is_active=True,
        )
        self.emp_manager.roles.add(self.role_manager)

        # --- Создаём тестовую собаку ---
        self.dog = ServiceDog.objects.create(
            name='Граф',
            inventory_number='КС-2024-001',
            breed='Немецкая овчарка',
            gender='Кобель',
            arrival_date=date(2020, 1, 15),
            status=self.status_active,
            main_kennel=self.emp_kennel,
        )

        # --- Клиент для HTTP-запросов в тестах ---
        self.client = Client()

        # --- Дата с часовым поясом для полей DateTimeField ---
        # timezone.make_aware добавляет часовой пояс к naive datetime,
        # чтобы не было предупреждения RuntimeWarning
        self.aware_datetime = timezone.make_aware(
            timezone.datetime(2024, 3, 1, 10, 0, 0)
        )


# ==============================================================================
# 1. ТЕСТЫ МОДЕЛЕЙ
# ==============================================================================

class ModelTests(BaseTestCase):
    """Проверяем создание записей и связи между моделями"""

    def test_dog_status_created(self):
        """Статус собаки создаётся корректно"""
        self.assertEqual(self.status_active.name, 'В работе')
        self.assertTrue(self.status_active.is_active)

    def test_dog_created(self):
        """Служебная собака создаётся и сохраняется в БД"""
        self.assertEqual(ServiceDog.objects.count(), 1)
        dog = ServiceDog.objects.get(inventory_number='КС-2024-001')
        self.assertEqual(dog.name, 'Граф')
        self.assertEqual(dog.breed, 'Немецкая овчарка')

    def test_dog_str(self):
        """Метод __str__ возвращает кличку и инвентарный номер"""
        self.assertEqual(str(self.dog), 'Граф (КС-2024-001)')

    def test_dog_status_relation(self):
        """Собака корректно связана со статусом"""
        self.assertEqual(self.dog.status.name, 'В работе')

    def test_dog_kennel_relation(self):
        """Собака корректно связана с кинологом"""
        self.assertEqual(self.dog.main_kennel.full_name, 'Петров Дмитрий Александрович')

    def test_dog_specialization_link(self):
        """Специализация корректно привязывается к собаке через промежуточную модель"""
        link = DogSpecializationLink.objects.create(
            dog=self.dog,
            specialization=self.spec_search,
            assignment_date=date(2020, 6, 1),
        )
        self.assertEqual(self.dog.specializations.count(), 1)
        self.assertEqual(link.specialization.name, 'Розыскная')

    def test_training_created(self):
        """Тренировка создаётся и связывается с собакой и кинологом"""
        training = Training.objects.create(
            dog=self.dog,
            kennel=self.emp_kennel,
            skill=self.skill,
            datetime=self.aware_datetime,
            duration=timedelta(hours=1),
        )
        self.assertEqual(Training.objects.count(), 1)
        self.assertEqual(training.dog.name, 'Граф')
        self.assertEqual(training.skill.name, 'Послушание')

    def test_vet_record_created(self):
        """Ветеринарная запись создаётся и связывается с собакой"""
        record = VeterinaryRecord.objects.create(
            dog=self.dog,
            veterinarian=self.emp_vet,
            procedure_type=self.proc_type,
            procedure_date=date(2024, 1, 15),
            description='Плановая вакцинация',
            is_routine=True,
        )
        self.assertEqual(VeterinaryRecord.objects.count(), 1)
        self.assertEqual(record.dog.name, 'Граф')
        self.assertTrue(record.is_routine)

    def test_employee_roles(self):
        """Сотруднику корректно назначается роль"""
        self.assertIn(self.role_kennel, self.emp_kennel.roles.all())
        self.assertNotIn(self.role_vet, self.emp_kennel.roles.all())

    def test_dog_cascade_delete(self):
        """При удалении собаки удаляются и её тренировки"""
        Training.objects.create(
            dog=self.dog,
            kennel=self.emp_kennel,
            skill=self.skill,
            datetime=self.aware_datetime,
            duration=timedelta(hours=1),
        )
        self.assertEqual(Training.objects.count(), 1)
        self.dog.delete()
        # После удаления собаки тренировка тоже должна исчезнуть
        self.assertEqual(Training.objects.count(), 0)

    def test_unique_inventory_number(self):
        """Два пса не могут иметь одинаковый инвентарный номер"""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            ServiceDog.objects.create(
                name='Рекс',
                inventory_number='КС-2024-001',  # уже существует
                breed='Лабрадор',
                gender='Кобель',
                arrival_date=date(2021, 1, 1),
                status=self.status_active,
            )


# ==============================================================================
# 2. ТЕСТЫ АВТОРИЗАЦИИ
# ==============================================================================

class AuthTests(BaseTestCase):
    """Проверяем вход, выход и обработку неверных данных"""

    def test_login_page_accessible(self):
        """Страница входа открывается без авторизации"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        """Успешный вход перенаправляет на дашборд"""
        response = self.client.post(reverse('login'), {
            'username': 'kennel_user',
            'password': 'testpass123',
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_wrong_password(self):
        """Неверный пароль — остаёмся на странице входа с ошибкой"""
        response = self.client.post(reverse('login'), {
            'username': 'kennel_user',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)

    def test_login_wrong_username(self):
        """Несуществующий логин — остаёмся на странице входа"""
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)

    def test_logout(self):
        """Выход из системы перенаправляет на страницу входа"""
        self.client.login(username='kennel_user', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_dashboard_requires_login(self):
        """Неавторизованный пользователь не может открыть дашборд"""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_already_logged_in_redirects_from_login(self):
        """Авторизованный пользователь при открытии /login/ попадает на дашборд"""
        self.client.login(username='kennel_user', password='testpass123')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('dashboard'))


# ==============================================================================
# 3. ТЕСТЫ РОЛЕЙ
# ==============================================================================

class RoleAccessTests(BaseTestCase):
    """Проверяем что каждая роль видит только свои разделы"""

    # --- Кинолог ---

    def test_kennel_can_access_dog_list(self):
        """Кинолог может открыть список собак"""
        self.client.login(username='kennel_user', password='testpass123')
        response = self.client.get(reverse('dog_list'))
        self.assertEqual(response.status_code, 200)

    def test_kennel_can_access_training_list(self):
        """Кинолог может открыть список тренировок"""
        self.client.login(username='kennel_user', password='testpass123')
        response = self.client.get(reverse('training_list'))
        self.assertEqual(response.status_code, 200)

    def test_kennel_cannot_access_vet_list(self):
        """Кинолог не может открыть ветеринарный раздел"""
        self.client.login(username='kennel_user', password='testpass123')
        response = self.client.get(reverse('vet_list'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_kennel_cannot_access_employee_list(self):
        """Кинолог не может открыть список сотрудников"""
        self.client.login(username='kennel_user', password='testpass123')
        response = self.client.get(reverse('employee_list'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_kennel_cannot_access_reports(self):
        """Кинолог не может открыть раздел отчётов"""
        self.client.login(username='kennel_user', password='testpass123')
        response = self.client.get(reverse('report_list'))
        self.assertRedirects(response, reverse('dashboard'))

    # --- Ветеринар ---

    def test_vet_can_access_vet_list(self):
        """Ветеринар может открыть ветеринарный раздел"""
        self.client.login(username='vet_user', password='testpass123')
        response = self.client.get(reverse('vet_list'))
        self.assertEqual(response.status_code, 200)

    def test_vet_cannot_access_dog_list(self):
        """Ветеринар не может открыть список собак"""
        self.client.login(username='vet_user', password='testpass123')
        response = self.client.get(reverse('dog_list'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_vet_cannot_access_reports(self):
        """Ветеринар не может открыть раздел отчётов"""
        self.client.login(username='vet_user', password='testpass123')
        response = self.client.get(reverse('report_list'))
        self.assertRedirects(response, reverse('dashboard'))

    # --- Руководитель ---

    def test_manager_can_access_dog_list(self):
        """Руководитель может открыть список собак"""
        self.client.login(username='manager_user', password='testpass123')
        response = self.client.get(reverse('dog_list'))
        self.assertEqual(response.status_code, 200)

    def test_manager_can_access_vet_list(self):
        """Руководитель может открыть ветеринарный раздел"""
        self.client.login(username='manager_user', password='testpass123')
        response = self.client.get(reverse('vet_list'))
        self.assertEqual(response.status_code, 200)

    def test_manager_can_access_employee_list(self):
        """Руководитель может открыть список сотрудников"""
        self.client.login(username='manager_user', password='testpass123')
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)

    def test_manager_can_access_reports(self):
        """Руководитель может открыть раздел отчётов"""
        self.client.login(username='manager_user', password='testpass123')
        response = self.client.get(reverse('report_list'))
        self.assertEqual(response.status_code, 200)


# ==============================================================================
# 4. ТЕСТЫ СТРАНИЦ
# ==============================================================================

class PageTests(BaseTestCase):
    """Проверяем коды ответов и перенаправления для всех страниц"""

    def setUp(self):
        super().setUp()
        # Логинимся как суперпользователь — у него доступ ко всем страницам
        # без ограничений по ролям, что важно для чистоты тестов страниц
        self.superuser = User.objects.create_superuser(
            username='admin_test',
            password='testpass123',
        )
        self.client.login(username='admin_test', password='testpass123')

    def test_dashboard_returns_200(self):
        """Дашборд открывается"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dog_list_returns_200(self):
        """Список собак открывается"""
        response = self.client.get(reverse('dog_list'))
        self.assertEqual(response.status_code, 200)

    def test_dog_detail_returns_200(self):
        """Карточка собаки открывается"""
        response = self.client.get(reverse('dog_detail', args=[self.dog.pk]))
        self.assertEqual(response.status_code, 200)

    def test_dog_detail_404_for_nonexistent(self):
        """Карточка несуществующей собаки возвращает 404"""
        response = self.client.get(reverse('dog_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_dog_add_returns_200(self):
        """Форма добавления собаки открывается"""
        response = self.client.get(reverse('dog_add'))
        self.assertEqual(response.status_code, 200)

    def test_training_list_returns_200(self):
        """Список тренировок открывается"""
        response = self.client.get(reverse('training_list'))
        self.assertEqual(response.status_code, 200)

    def test_training_add_returns_200(self):
        """Форма добавления тренировки открывается"""
        response = self.client.get(reverse('training_add'))
        self.assertEqual(response.status_code, 200)

    def test_event_list_returns_200(self):
        """Список мероприятий открывается"""
        response = self.client.get(reverse('event_list'))
        self.assertEqual(response.status_code, 200)

    def test_event_add_returns_200(self):
        """Форма добавления мероприятия открывается"""
        response = self.client.get(reverse('event_add'))
        self.assertEqual(response.status_code, 200)

    def test_vet_list_returns_200(self):
        """Список ветеринарных записей открывается"""
        response = self.client.get(reverse('vet_list'))
        self.assertEqual(response.status_code, 200)

    def test_vet_add_returns_200(self):
        """Форма добавления ветеринарной записи открывается"""
        response = self.client.get(reverse('vet_add'))
        self.assertEqual(response.status_code, 200)

    def test_employee_list_returns_200(self):
        """Список сотрудников открывается"""
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)

    def test_report_list_returns_200(self):
        """Раздел отчётов открывается"""
        response = self.client.get(reverse('report_list'))
        self.assertEqual(response.status_code, 200)

    def test_dog_search_works(self):
        """Поиск по списку собак работает и возвращает 200"""
        response = self.client.get(reverse('dog_list') + '?search=Граф')
        self.assertEqual(response.status_code, 200)

    def test_dog_filter_by_status(self):
        """Фильтрация собак по статусу работает"""
        response = self.client.get(
            reverse('dog_list') + f'?status={self.status_active.pk}'
        )
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_redirects_to_login(self):
        """Неавторизованный запрос на любую страницу — редирект на login"""
        self.client.logout()
        for url_name in ['dashboard', 'dog_list', 'training_list', 'vet_list']:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 302,
                msg=f'Страница {url_name} должна перенаправлять неавторизованных')