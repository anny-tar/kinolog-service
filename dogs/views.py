from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (
    ServiceDog, Training, ServiceEvent,
    VeterinaryRecord, Employee, ReportTemplate,
    DogStatus, TrainingSkill, EventType, VeterinaryProcedureType
)
from .forms import ServiceDogForm, TrainingForm, ServiceEventForm, VeterinaryRecordForm
from .decorators import role_required


# ==============================================================================
# АВТОРИЗАЦИЯ
# ==============================================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            error = 'Неверный логин или пароль'
    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


# ==============================================================================
# ДАШБОРД
# ==============================================================================

@login_required(login_url='login')
def dashboard(request):
    context = {
        'total_dogs': ServiceDog.objects.count(),
        'active_dogs': ServiceDog.objects.filter(status__name='В работе').count(),
        'total_employees': Employee.objects.filter(is_active=True).count(),
        'recent_trainings': Training.objects.select_related('dog', 'kennel', 'skill').order_by('-datetime')[:5],
        'upcoming_vet': VeterinaryRecord.objects.filter(
            next_procedure_date__isnull=False
        ).select_related('dog', 'procedure_type').order_by('next_procedure_date')[:5],
    }
    return render(request, 'dogs/dashboard.html', context)


# ==============================================================================
# СОБАКИ
# ==============================================================================

@login_required(login_url='login')
@role_required('Кинолог', 'Руководитель')
def dog_list(request):
    dogs = ServiceDog.objects.select_related('status', 'main_kennel').all()
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    if search:
        dogs = dogs.filter(name__icontains=search) | dogs.filter(inventory_number__icontains=search)
    if status_filter:
        dogs = dogs.filter(status_id=status_filter)
    return render(request, 'dogs/dog_list.html', {
        'dogs': dogs,
        'statuses': DogStatus.objects.filter(is_active=True),
        'search': search,
        'status_filter': status_filter,
    })


@login_required(login_url='login')
@role_required('Кинолог', 'Руководитель', 'Ветеринар')
def dog_detail(request, pk):
    dog = get_object_or_404(ServiceDog, pk=pk)
    return render(request, 'dogs/dog_detail.html', {
        'dog': dog,
        'trainings': dog.trainings.select_related('skill', 'kennel').order_by('-datetime')[:10],
        'vet_records': dog.vet_records.select_related('procedure_type', 'veterinarian').order_by('-procedure_date')[:10],
        'events': dog.events.select_related('event_type', 'kennel').order_by('-datetime')[:10],
        'equipment': dog.equipment.select_related('equipment_type').all(),
        'specializations': dog.dogspecializationlink_set.select_related('specialization').all(),
    })


@login_required(login_url='login')
@role_required('Руководитель')
def dog_add(request):
    """Добавление новой собаки"""
    form = ServiceDogForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        dog = form.save()
        messages.success(request, f'Собака «{dog.name}» успешно добавлена!')
        return redirect('dog_detail', pk=dog.pk)
    return render(request, 'dogs/dog_form.html', {'form': form, 'title': 'Добавить собаку'})


@login_required(login_url='login')
@role_required('Руководитель')
def dog_edit(request, pk):
    """Редактирование карточки собаки"""
    dog = get_object_or_404(ServiceDog, pk=pk)
    form = ServiceDogForm(request.POST or None, request.FILES or None, instance=dog)
    if form.is_valid():
        form.save()
        messages.success(request, f'Данные собаки «{dog.name}» обновлены!')
        return redirect('dog_detail', pk=dog.pk)
    return render(request, 'dogs/dog_form.html', {'form': form, 'title': f'Редактировать: {dog.name}', 'dog': dog})


# ==============================================================================
# ТРЕНИРОВКИ
# ==============================================================================

@login_required(login_url='login')
@role_required('Кинолог', 'Руководитель')
def training_list(request):
    trainings = Training.objects.select_related('dog', 'kennel', 'skill').order_by('-datetime')
    search = request.GET.get('search', '')
    skill_filter = request.GET.get('skill', '')
    if search:
        trainings = trainings.filter(dog__name__icontains=search)
    if skill_filter:
        trainings = trainings.filter(skill_id=skill_filter)
    return render(request, 'dogs/training_list.html', {
        'trainings': trainings,
        'skills': TrainingSkill.objects.filter(is_active=True),
        'search': search,
        'skill_filter': skill_filter,
    })


@login_required(login_url='login')
@role_required('Кинолог', 'Руководитель')
def training_add(request):
    """Добавление тренировки"""
    form = TrainingForm(request.POST or None, user=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Тренировка успешно добавлена!')
        return redirect('training_list')
    return render(request, 'dogs/training_form.html', {'form': form, 'title': 'Добавить тренировку'})


# ==============================================================================
# СЛУЖЕБНЫЕ МЕРОПРИЯТИЯ
# ==============================================================================

@login_required(login_url='login')
@role_required('Кинолог', 'Руководитель')
def event_list(request):
    events = ServiceEvent.objects.select_related('dog', 'kennel', 'event_type').order_by('-datetime')
    search = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    if search:
        events = events.filter(dog__name__icontains=search) | events.filter(location__icontains=search)
    if type_filter:
        events = events.filter(event_type_id=type_filter)
    return render(request, 'dogs/event_list.html', {
        'events': events,
        'event_types': EventType.objects.filter(is_active=True),
        'search': search,
        'type_filter': type_filter,
    })


@login_required(login_url='login')
@role_required('Кинолог', 'Руководитель')
def event_add(request):
    form = ServiceEventForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Мероприятие успешно добавлено!')
        return redirect('event_list')
    return render(request, 'dogs/event_form.html', {'form': form, 'title': 'Добавить мероприятие'})


# ==============================================================================
# ВЕТЕРИНАРИЯ
# ==============================================================================

@login_required(login_url='login')
@role_required('Ветеринар', 'Руководитель')
def vet_list(request):
    records = VeterinaryRecord.objects.select_related(
        'dog', 'procedure_type', 'veterinarian'
    ).order_by('-procedure_date')
    search = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    if search:
        records = records.filter(dog__name__icontains=search)
    if type_filter:
        records = records.filter(procedure_type_id=type_filter)
    return render(request, 'dogs/vet_list.html', {
        'records': records,
        'procedure_types': VeterinaryProcedureType.objects.filter(is_active=True),
        'search': search,
        'type_filter': type_filter,
    })


@login_required(login_url='login')
@role_required('Ветеринар', 'Руководитель')
def vet_add(request):
    form = VeterinaryRecordForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Ветеринарная запись добавлена!')
        return redirect('vet_list')
    return render(request, 'dogs/vet_form.html', {'form': form, 'title': 'Добавить ветеринарную запись'})


# ==============================================================================
# СОТРУДНИКИ
# ==============================================================================

@login_required(login_url='login')
@role_required('Руководитель')
def employee_list(request):
    employees = Employee.objects.prefetch_related('roles').filter(is_active=True)
    return render(request, 'dogs/employee_list.html', {'employees': employees})

@login_required(login_url='login')
@role_required('Кинолог', 'Руководитель')
def training_edit(request, pk):
    training = get_object_or_404(Training, pk=pk)
    form = TrainingForm(request.POST or None, instance=training, user=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Тренировка успешно обновлена!')
        return redirect('training_list')
    return render(request, 'dogs/training_form.html', {
        'form': form,
        'title': f'Редактировать тренировку: {training.dog.name}',
    })


@login_required(login_url='login')
@role_required('Кинолог', 'Руководитель')
def event_edit(request, pk):
    event = get_object_or_404(ServiceEvent, pk=pk)
    form = ServiceEventForm(request.POST or None, request.FILES or None, instance=event)
    if form.is_valid():
        form.save()
        messages.success(request, 'Мероприятие успешно обновлено!')
        return redirect('event_list')
    return render(request, 'dogs/event_form.html', {
        'form': form,
        'title': f'Редактировать мероприятие: {event.dog.name}',
    })


@login_required(login_url='login')
@role_required('Ветеринар', 'Руководитель')
def vet_edit(request, pk):
    record = get_object_or_404(VeterinaryRecord, pk=pk)
    form = VeterinaryRecordForm(request.POST or None, instance=record)
    if form.is_valid():
        form.save()
        messages.success(request, 'Ветеринарная запись обновлена!')
        return redirect('vet_list')
    return render(request, 'dogs/vet_form.html', {
        'form': form,
        'title': f'Редактировать запись: {record.dog.name}',
    })


@login_required(login_url='login')
@role_required('Руководитель')
def employee_add(request):
    from .forms import EmployeeForm
    form = EmployeeForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        employee = form.save()
        messages.success(request, f'Сотрудник «{employee.full_name}» успешно добавлен!')
        return redirect('employee_list')
    return render(request, 'dogs/employee_form.html', {
        'form': form,
        'title': 'Добавить сотрудника',
    })


@login_required(login_url='login')
@role_required('Руководитель')
def employee_edit(request, pk):
    from .forms import EmployeeForm
    employee = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, request.FILES or None, instance=employee)
    if form.is_valid():
        form.save()
        messages.success(request, f'Данные сотрудника «{employee.full_name}» обновлены!')
        return redirect('employee_list')
    return render(request, 'dogs/employee_form.html', {
        'form': form,
        'title': f'Редактировать: {employee.full_name}',
    })

# ==============================================================================
# ОТЧЁТЫ
# ==============================================================================

@login_required(login_url='login')
@role_required('Руководитель')
def report_list(request):
    templates = ReportTemplate.objects.all()
    return render(request, 'dogs/report_list.html', {'templates': templates})


from django.http import HttpResponse
from datetime import date, timedelta
from .report_generator import (
    generate_dogs_report,
    generate_trainings_report,
    generate_vet_report,
    generate_events_report,
)

# Словарь доступных отчётов: ключ → (название, функция, нужны ли даты)
REPORT_TYPES = {
    'dogs':      ('Список служебных собак',          generate_dogs_report,      False),
    'trainings': ('Журнал тренировочных занятий',    generate_trainings_report, True),
    'vet':       ('Ветеринарные мероприятия',         generate_vet_report,       True),
    'events':    ('Служебные мероприятия',            generate_events_report,    True),
}


@login_required(login_url='login')
@role_required('Руководитель')
def report_list(request):
    """Страница выбора и генерации отчётов"""

    # Значения по умолчанию для дат: текущий месяц
    today = date.today()
    default_from = today.replace(day=1)  # первое число текущего месяца
    default_to = today

    context = {
        'report_types': REPORT_TYPES,
        'default_from': default_from.strftime('%Y-%m-%d'),
        'default_to': default_to.strftime('%Y-%m-%d'),
    }
    return render(request, 'dogs/report_list.html', context)


@login_required(login_url='login')
@role_required('Руководитель')
def report_generate(request):
    """Генерирует и отдаёт файл .docx пользователю"""

    if request.method != 'POST':
        return redirect('report_list')

    report_type = request.POST.get('report_type')

    if report_type not in REPORT_TYPES:
        messages.error(request, 'Неизвестный тип отчёта.')
        return redirect('report_list')

    report_name, generator_func, needs_dates = REPORT_TYPES[report_type]

    # Если отчёт требует период — читаем даты из формы
    if needs_dates:
        try:
            date_from = date.fromisoformat(request.POST.get('date_from'))
            date_to = date.fromisoformat(request.POST.get('date_to'))
        except (ValueError, TypeError):
            messages.error(request, 'Неверный формат дат.')
            return redirect('report_list')
        buffer = generator_func(date_from, date_to)
        filename = f'{report_type}_{date_from}_{date_to}.docx'
    else:
        buffer = generator_func()
        filename = f'{report_type}_{date.today()}.docx'

    # Отдаём файл пользователю как скачивание
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response