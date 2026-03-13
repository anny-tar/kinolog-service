from django.contrib import admin
from .models import (
    Role, Employee,
    DogStatus, DogSpecialization, TrainingSkill,
    EventType, EquipmentType, VeterinaryProcedureType,
    ServiceDog, DogSpecializationLink,
    Training, ServiceEvent, Equipment,
    VeterinaryRecord, ReportTemplate,
)


# ==============================================================================
# ВСПОМОГАТЕЛЬНЫЙ КЛАСС — общие настройки для справочников
# Чтобы не повторять одно и то же для каждого справочника
# ==============================================================================

class ActiveFilterMixin:
    """Добавляет фильтр по полю 'Активен' в правую панель"""
    list_filter = ('is_active',)


# ==============================================================================
# МОДУЛЬ "АДМИНИСТРИРОВАНИЕ"
# ==============================================================================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)  # колонки в списке записей


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    # Колонки в таблице списка сотрудников
    list_display = ('full_name', 'rank', 'position', 'department', 'phone', 'is_active')

    # Фильтры в правой панели
    list_filter = ('is_active', 'roles')

    # Поиск по этим полям (строка поиска вверху)
    search_fields = ('full_name', 'rank', 'position', 'department')

    # Поля, которые можно редактировать прямо в списке (без входа в запись)
    list_editable = ('is_active',)

    # Группировка полей внутри формы редактирования
    fieldsets = (
        ('Личные данные', {
            'fields': ('user', 'full_name', 'photo', 'rank', 'position', 'phone')
        }),
        ('Служебная информация', {
            'fields': ('department', 'hire_date', 'certification_date', 'roles')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )


# ==============================================================================
# СПРАВОЧНИКИ
# ==============================================================================

@admin.register(DogStatus)
class DogStatusAdmin(ActiveFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)


@admin.register(DogSpecialization)
class DogSpecializationAdmin(ActiveFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)


@admin.register(TrainingSkill)
class TrainingSkillAdmin(ActiveFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)


@admin.register(EventType)
class EventTypeAdmin(ActiveFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)


@admin.register(EquipmentType)
class EquipmentTypeAdmin(ActiveFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)


@admin.register(VeterinaryProcedureType)
class VeterinaryProcedureTypeAdmin(ActiveFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)


# ==============================================================================
# МОДУЛЬ "КИНОЛОГ"
# ==============================================================================

class DogSpecializationLinkInline(admin.TabularInline):
    """
    Inline позволяет редактировать специализации прямо
    на странице собаки — не переходя в отдельный раздел.
    TabularInline = отображение в виде таблицы.
    """
    model = DogSpecializationLink
    extra = 1   # сколько пустых строк показывать для добавления


class TrainingInline(admin.TabularInline):
    """Тренировки собаки — прямо на странице собаки"""
    model = Training
    extra = 0   # не показываем пустые строки (тренировок обычно много)
    fields = ('datetime', 'skill', 'kennel', 'score', 'duration')
    # show_change_link — ссылка для открытия полной формы записи
    show_change_link = True


class EquipmentInline(admin.TabularInline):
    """Снаряжение собаки — прямо на странице собаки"""
    model = Equipment
    extra = 1
    fields = ('equipment_type', 'issue_date', 'current_condition')


class VetRecordInline(admin.TabularInline):
    """Ветеринарные записи собаки — прямо на странице собаки"""
    model = VeterinaryRecord
    extra = 0
    fields = ('procedure_date', 'procedure_type', 'veterinarian', 'is_routine', 'next_procedure_date')
    show_change_link = True


@admin.register(ServiceDog)
class ServiceDogAdmin(admin.ModelAdmin):
    list_display = ('name', 'inventory_number', 'breed', 'gender', 'status', 'main_kennel')
    list_filter = ('status', 'gender', 'breed')
    search_fields = ('name', 'inventory_number', 'breed')

    # Подключаем inline-блоки на страницу собаки
    inlines = [
        DogSpecializationLinkInline,
        EquipmentInline,
        TrainingInline,
        VetRecordInline,
    ]

    fieldsets = (
        ('Основные данные', {
            'fields': ('name', 'inventory_number', 'photo', 'breed', 'gender', 'birth_date')
        }),
        ('Служебная информация', {
            'fields': ('status', 'main_kennel', 'arrival_date')
        }),
        ('Описание', {
            'fields': ('color_marks', 'origin_story'),
            # classes: collapse — блок свёрнут по умолчанию
            'classes': ('collapse',),
        }),
    )


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'dog', 'kennel', 'skill', 'score', 'duration')
    list_filter = ('skill', 'kennel', 'datetime')
    search_fields = ('dog__name', 'kennel__full_name', 'comments')
    # dog__name — поиск по полю name связанной модели ServiceDog


@admin.register(ServiceEvent)
class ServiceEventAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'dog', 'kennel', 'event_type', 'location')
    list_filter = ('event_type', 'kennel', 'datetime')
    search_fields = ('dog__name', 'location', 'results')


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('dog', 'equipment_type', 'issue_date', 'current_condition')
    list_filter = ('equipment_type',)
    search_fields = ('dog__name',)


# ==============================================================================
# МОДУЛЬ "ВЕТЕРИНАРНЫЙ"
# ==============================================================================

@admin.register(VeterinaryRecord)
class VeterinaryRecordAdmin(admin.ModelAdmin):
    list_display = ('procedure_date', 'dog', 'procedure_type', 'veterinarian', 'is_routine', 'next_procedure_date')
    list_filter = ('procedure_type', 'is_routine', 'veterinarian')
    search_fields = ('dog__name', 'description')

    # Выделяем цветом просроченные процедуры — добавим позже


# ==============================================================================
# МОДУЛЬ "РУКОВОДИТЕЛЬ"
# ==============================================================================

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'created_date')
    search_fields = ('name', 'report_type')