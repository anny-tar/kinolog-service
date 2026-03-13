# Формы Django автоматически генерируют HTML-поля и проверяют введённые данные

from django import forms
from django.contrib.auth.models import User
from .models import (
    ServiceDog, Training, ServiceEvent,
    VeterinaryRecord, Equipment, Employee,
    DogStatus, DogSpecialization, TrainingSkill,
    EventType, EquipmentType, VeterinaryProcedureType,
    Role,
)


class ServiceDogForm(forms.ModelForm):
    """Форма добавления/редактирования служебной собаки"""

    class Meta:
        model = ServiceDog
        fields = [
            'name', 'inventory_number', 'breed', 'gender',
            'birth_date', 'arrival_date', 'status', 'main_kennel',
            'color_marks', 'origin_story', 'photo'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Кличка'}),
            'inventory_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Инвентарный номер'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Порода'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'birth_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'arrival_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'main_kennel': forms.Select(attrs={'class': 'form-select'}),
            'color_marks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'origin_story': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].queryset = DogStatus.objects.filter(is_active=True)
        self.fields['main_kennel'].queryset = Employee.objects.filter(is_active=True)
        self.fields['main_kennel'].required = False
        self.fields['birth_date'].required = False
        self.fields['color_marks'].required = False
        self.fields['origin_story'].required = False


class TrainingForm(forms.ModelForm):
    """Форма добавления/редактирования тренировки"""

    class Meta:
        model = Training
        fields = ['dog', 'kennel', 'skill', 'datetime', 'duration', 'weather_conditions', 'score', 'comments']
        widgets = {
            'dog': forms.Select(attrs={'class': 'form-select'}),
            'kennel': forms.Select(attrs={'class': 'form-select'}),
            'skill': forms.Select(attrs={'class': 'form-select'}),
            'datetime': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 01:30:00'}),
            'weather_conditions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ясно, +15°C'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['skill'].queryset = TrainingSkill.objects.filter(is_active=True)
        self.fields['kennel'].queryset = Employee.objects.filter(is_active=True)
        self.fields['score'].required = False
        self.fields['comments'].required = False
        self.fields['weather_conditions'].required = False


class ServiceEventForm(forms.ModelForm):
    """Форма добавления/редактирования служебного мероприятия"""

    class Meta:
        model = ServiceEvent
        fields = ['dog', 'kennel', 'event_type', 'datetime', 'location', 'duration', 'results', 'documents']
        widgets = {
            'dog': forms.Select(attrs={'class': 'form-select'}),
            'kennel': forms.Select(attrs={'class': 'form-select'}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'datetime': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес или описание места'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 02:00:00'}),
            'results': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'documents': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event_type'].queryset = EventType.objects.filter(is_active=True)
        self.fields['kennel'].queryset = Employee.objects.filter(is_active=True)
        self.fields['results'].required = False
        self.fields['documents'].required = False


class VeterinaryRecordForm(forms.ModelForm):
    """Форма добавления/редактирования ветеринарной записи"""

    class Meta:
        model = VeterinaryRecord
        fields = ['dog', 'veterinarian', 'procedure_type', 'procedure_date',
                  'next_procedure_date', 'is_routine', 'description', 'notes']
        widgets = {
            'dog': forms.Select(attrs={'class': 'form-select'}),
            'veterinarian': forms.Select(attrs={'class': 'form-select'}),
            'procedure_type': forms.Select(attrs={'class': 'form-select'}),
            'procedure_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'next_procedure_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'is_routine': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['procedure_type'].queryset = VeterinaryProcedureType.objects.filter(is_active=True)
        self.fields['veterinarian'].queryset = Employee.objects.filter(is_active=True)
        self.fields['next_procedure_date'].required = False
        self.fields['notes'].required = False


class EmployeeForm(forms.ModelForm):
    """
    Форма добавления/редактирования сотрудника.
    Включает поля карточки + поля учётной записи Django (логин, пароль).
    """

    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин для входа в систему'}),
    )
    password = forms.CharField(
        label='Пароль',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Оставьте пустым чтобы не менять'}),
        help_text='При редактировании оставьте пустым, если не хотите менять пароль',
    )
    roles = forms.ModelMultipleChoiceField(
        label='Роли',
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=True,
    )

    class Meta:
        model = Employee
        fields = [
            'full_name', 'rank', 'position', 'department',
            'phone', 'hire_date', 'certification_date',
            'is_active', 'photo',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия Имя Отчество'}),
            'rank': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Звание'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Должность'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Подразделение'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (846) 000-00-00'}),
            'hire_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'certification_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # ClearableFileInput — обрабатывает удаление файла через photo-clear чекбокс
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        self.fields['department'].required = False
        self.fields['phone'].required = False
        self.fields['hire_date'].required = False
        self.fields['certification_date'].required = False
        self.fields['photo'].required = False

        if instance and instance.pk:
            self.fields['username'].initial = instance.user.username
            self.fields['roles'].initial = instance.roles.all()

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')
        return username

    def save(self, commit=True):
        employee = super().save(commit=False)
        username = self.cleaned_data['username']
        password = self.cleaned_data.get('password')
        roles    = self.cleaned_data['roles']

        if employee.pk:
            user = employee.user
            user.username = username
            if password:
                user.set_password(password)
            user.save()
        else:
            user = User.objects.create_user(
                username=username,
                password=password or 'Pass1234!',
            )
            employee.user = user

        if commit:
            employee.save()
            # save_m2m() вызывает финальную обработку всех полей включая
            # ClearableFileInput — без этого удаление файла не применяется
            self.save_m2m()
            employee.roles.set(roles)

        return employee