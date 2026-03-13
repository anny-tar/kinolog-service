from django.db import models
from django.contrib.auth.models import User  # стандартная модель пользователя Django


# ==============================================================================
# МОДУЛЬ "АДМИНИСТРИРОВАНИЕ" — роли и сотрудники
# Размещаем первыми, т.к. на них ссылаются другие модели
# ==============================================================================

class Role(models.Model):
    """Роль сотрудника в системе: Кинолог, Ветеринар, Руководитель"""

    # Константы для поля name — чтобы не писать строки вручную в разных местах
    KENNEL_OFFICER = 'Кинолог'
    VETERINARIAN = 'Ветеринар'
    MANAGER = 'Руководитель'

    ROLE_CHOICES = [
        (KENNEL_OFFICER, 'Кинолог'),
        (VETERINARIAN, 'Ветеринар'),
        (MANAGER, 'Руководитель'),
    ]

    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True,          # каждая роль существует только один раз
        verbose_name='Название роли'
    )

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name  # что показывать в админке и шаблонах


class Employee(models.Model):
    """Сотрудник кинологической службы"""

    # Связь с системным пользователем Django (для входа в систему)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,  # если удалить User — сотрудник останется
        null=True,
        blank=True,
        verbose_name='Учётная запись'
    )

    full_name = models.CharField(max_length=200, verbose_name='ФИО')
    rank = models.CharField(max_length=100, verbose_name='Звание')
    position = models.CharField(max_length=200, verbose_name='Должность')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    department = models.CharField(max_length=200, blank=True, verbose_name='Подразделение')

    # upload_to — папка внутри media/ куда сохраняются файлы
    photo = models.ImageField(
        upload_to='employees/photos/',
        null=True,
        blank=True,
        verbose_name='Фотография'
    )

    hire_date = models.DateField(null=True, blank=True, verbose_name='Дата приёма')
    certification_date = models.DateField(null=True, blank=True, verbose_name='Дата аттестации')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    # Сотрудник может иметь несколько ролей (например, кинолог + руководитель)
    roles = models.ManyToManyField(Role, blank=True, verbose_name='Роли')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['full_name']  # сортировка по умолчанию — по алфавиту

    def __str__(self):
        return f'{self.full_name} ({self.rank})'


# ==============================================================================
# СПРАВОЧНИКИ — простые таблицы с названием и флагом активности
# ==============================================================================

class DogStatus(models.Model):
    """Справочник статусов собаки: В работе, На лечении, В резерве и т.д."""

    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Статус собаки'
        verbose_name_plural = 'Статусы собак'

    def __str__(self):
        return self.name


class DogSpecialization(models.Model):
    """Справочник специализаций: Розыскная, Поиск ВВ, Поиск наркотиков и т.д."""

    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Специализация'
        verbose_name_plural = 'Специализации'

    def __str__(self):
        return self.name


class TrainingSkill(models.Model):
    """Справочник навыков тренировки: Послушание, Поиск по следу, Задержание и т.д."""

    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Навык тренировки'
        verbose_name_plural = 'Навыки тренировок'

    def __str__(self):
        return self.name


class EventType(models.Model):
    """Справочник типов мероприятий: Охрана порядка, Осмотр объекта и т.д."""

    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Тип мероприятия'
        verbose_name_plural = 'Типы мероприятий'

    def __str__(self):
        return self.name


class EquipmentType(models.Model):
    """Справочник типов снаряжения: Ошейник, Поводок, Намордник и т.д."""

    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Тип снаряжения'
        verbose_name_plural = 'Типы снаряжения'

    def __str__(self):
        return self.name


class VeterinaryProcedureType(models.Model):
    """Справочник ветеринарных процедур: Вакцинация, Обработка, Осмотр и т.д."""

    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Тип ветеринарной процедуры'
        verbose_name_plural = 'Типы ветеринарных процедур'

    def __str__(self):
        return self.name


# ==============================================================================
# МОДУЛЬ "КИНОЛОГ" — основные сущности
# ==============================================================================

class ServiceDog(models.Model):
    """Служебная собака — центральная сущность всей системы"""

    MALE = 'Кобель'
    FEMALE = 'Сука'
    GENDER_CHOICES = [
        (MALE, 'Кобель'),
        (FEMALE, 'Сука'),
    ]

    name = models.CharField(max_length=100, verbose_name='Кличка')
    inventory_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Инвентарный номер'
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    breed = models.CharField(max_length=100, verbose_name='Порода')
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name='Пол'
    )
    color_marks = models.TextField(blank=True, verbose_name='Окрас и приметы')
    arrival_date = models.DateField(verbose_name='Дата поступления')
    photo = models.ImageField(
        upload_to='dogs/photos/',
        null=True,
        blank=True,
        verbose_name='Фотография'
    )
    origin_story = models.TextField(blank=True, verbose_name='История происхождения')

    # ForeignKey — связь "многие к одному": много собак могут иметь один статус
    # on_delete=PROTECT — нельзя удалить статус, пока есть собаки с ним
    status = models.ForeignKey(
        DogStatus,
        on_delete=models.PROTECT,
        verbose_name='Статус'
    )

    # Основной кинолог, закреплённый за собакой
    main_kennel = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_dogs',  # обратное имя для запросов: employee.assigned_dogs.all()
        verbose_name='Основной кинолог'
    )

    # ManyToMany через промежуточную модель — чтобы хранить дату получения специализации
    specializations = models.ManyToManyField(
        DogSpecialization,
        through='DogSpecializationLink',  # указываем промежуточную модель
        blank=True,
        verbose_name='Специализации'
    )

    class Meta:
        verbose_name = 'Служебная собака'
        verbose_name_plural = 'Служебные собаки'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.inventory_number})'


class DogSpecializationLink(models.Model):
    """
    Промежуточная таблица связи собака-специализация.
    Нужна чтобы хранить дополнительное поле — дату получения специализации.
    """

    dog = models.ForeignKey(ServiceDog, on_delete=models.CASCADE, verbose_name='Собака')
    specialization = models.ForeignKey(DogSpecialization, on_delete=models.CASCADE, verbose_name='Специализация')
    assignment_date = models.DateField(verbose_name='Дата получения специализации')

    class Meta:
        verbose_name = 'Специализация собаки'
        verbose_name_plural = 'Специализации собак'
        # Уникальность пары: одна собака не может дважды получить одну специализацию
        unique_together = ('dog', 'specialization')

    def __str__(self):
        return f'{self.dog.name} — {self.specialization.name}'


class Training(models.Model):
    """Тренировочное занятие"""

    datetime = models.DateTimeField(verbose_name='Дата и время')
    # DurationField хранит продолжительность в формате HH:MM:SS
    duration = models.DurationField(verbose_name='Продолжительность')
    weather_conditions = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Погодные условия'
    )
    score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Оценка'
    )
    comments = models.TextField(blank=True, verbose_name='Комментарии')

    kennel = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='trainings',
        verbose_name='Кинолог'
    )
    dog = models.ForeignKey(
        ServiceDog,
        on_delete=models.CASCADE,  # удалим собаку — удалятся и её тренировки
        related_name='trainings',
        verbose_name='Собака'
    )
    skill = models.ForeignKey(
        TrainingSkill,
        on_delete=models.PROTECT,
        verbose_name='Навык'
    )

    class Meta:
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'
        ordering = ['-datetime']  # минус = сначала новые

    def __str__(self):
        return f'Тренировка {self.dog.name} — {self.datetime.strftime("%d.%m.%Y")}'


class ServiceEvent(models.Model):
    """Служебное мероприятие — реальное применение собаки"""

    datetime = models.DateTimeField(verbose_name='Дата и время')
    location = models.CharField(max_length=300, verbose_name='Место проведения')
    duration = models.DurationField(verbose_name='Продолжительность')
    results = models.TextField(blank=True, verbose_name='Результаты')
    # FileField для прикрепления документов
    documents = models.FileField(
        upload_to='events/documents/',
        null=True,
        blank=True,
        verbose_name='Документы'
    )

    event_type = models.ForeignKey(
        EventType,
        on_delete=models.PROTECT,
        verbose_name='Тип мероприятия'
    )
    kennel = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='events',
        verbose_name='Кинолог'
    )
    dog = models.ForeignKey(
        ServiceDog,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Собака'
    )

    class Meta:
        verbose_name = 'Служебное мероприятие'
        verbose_name_plural = 'Служебные мероприятия'
        ordering = ['-datetime']

    def __str__(self):
        return f'{self.event_type.name} — {self.dog.name} ({self.datetime.strftime("%d.%m.%Y")})'


class Equipment(models.Model):
    """Снаряжение, выданное собаке"""

    issue_date = models.DateField(verbose_name='Дата выдачи')
    current_condition = models.CharField(max_length=200, verbose_name='Текущее состояние')
    notes = models.TextField(blank=True, verbose_name='Примечания')

    dog = models.ForeignKey(
        ServiceDog,
        on_delete=models.CASCADE,
        related_name='equipment',
        verbose_name='Собака'
    )
    equipment_type = models.ForeignKey(
        EquipmentType,
        on_delete=models.PROTECT,
        verbose_name='Тип снаряжения'
    )

    class Meta:
        verbose_name = 'Снаряжение'
        verbose_name_plural = 'Снаряжение'

    def __str__(self):
        return f'{self.equipment_type.name} — {self.dog.name}'


# ==============================================================================
# МОДУЛЬ "ВЕТЕРИНАРНЫЙ"
# ==============================================================================

class VeterinaryRecord(models.Model):
    """Ветеринарная запись — медицинская история собаки"""

    procedure_date = models.DateField(verbose_name='Дата процедуры')
    description = models.TextField(verbose_name='Описание')
    next_procedure_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата следующей процедуры'
    )
    is_routine = models.BooleanField(default=True, verbose_name='Плановая процедура')
    notes = models.TextField(blank=True, verbose_name='Примечания')

    dog = models.ForeignKey(
        ServiceDog,
        on_delete=models.CASCADE,
        related_name='vet_records',
        verbose_name='Собака'
    )
    procedure_type = models.ForeignKey(
        VeterinaryProcedureType,
        on_delete=models.PROTECT,
        verbose_name='Тип процедуры'
    )
    veterinarian = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='vet_records',
        verbose_name='Ветеринар'
    )

    class Meta:
        verbose_name = 'Ветеринарная запись'
        verbose_name_plural = 'Ветеринарные записи'
        ordering = ['-procedure_date']

    def __str__(self):
        return f'{self.procedure_type.name} — {self.dog.name} ({self.procedure_date})'


# ==============================================================================
# МОДУЛЬ "РУКОВОДИТЕЛЬ" — отчётность
# ==============================================================================

class ReportTemplate(models.Model):
    """Шаблон отчёта в формате .docx"""

    name = models.CharField(max_length=200, verbose_name='Название шаблона')
    report_type = models.CharField(max_length=100, verbose_name='Тип отчёта')
    template_file = models.FileField(
        upload_to='reports/templates/',
        verbose_name='Файл шаблона'
    )
    created_date = models.DateField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Шаблон отчёта'
        verbose_name_plural = 'Шаблоны отчётов'

    def __str__(self):
        return self.name