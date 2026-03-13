# Формы Django автоматически генерируют HTML-поля и проверяют введённые данные

from django import forms
from .models import (
    ServiceDog, Training, ServiceEvent,
    VeterinaryRecord, Equipment, Employee,
    DogStatus, DogSpecialization, TrainingSkill,
    EventType, EquipmentType, VeterinaryProcedureType,
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
            # Виджеты определяют как поле выглядит в HTML
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Кличка'}),
            'inventory_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Инвентарный номер'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Порода'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'arrival_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'main_kennel': forms.Select(attrs={'class': 'form-select'}),
            'color_marks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'origin_story': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только активные статусы в выпадающем списке
        self.fields['status'].queryset = DogStatus.objects.filter(is_active=True)
        # Показываем только активных сотрудников
        self.fields['main_kennel'].queryset = Employee.objects.filter(is_active=True)
        self.fields['main_kennel'].required = False


class TrainingForm(forms.ModelForm):
    """Форма добавления тренировки"""

    class Meta:
        model = Training
        fields = ['dog', 'kennel', 'skill', 'datetime', 'duration', 'weather_conditions', 'score', 'comments']
        widgets = {
            'dog': forms.Select(attrs={'class': 'form-select'}),
            'kennel': forms.Select(attrs={'class': 'form-select'}),
            'skill': forms.Select(attrs={'class': 'form-select'}),
            'datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 01:30:00'}),
            'weather_conditions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ясно, +15°C'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Принимаем текущего пользователя чтобы ограничить список собак
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['skill'].queryset = TrainingSkill.objects.filter(is_active=True)
        self.fields['kennel'].queryset = Employee.objects.filter(is_active=True)
        self.fields['score'].required = False
        self.fields['comments'].required = False
        self.fields['weather_conditions'].required = False


class ServiceEventForm(forms.ModelForm):
    """Форма добавления служебного мероприятия"""

    class Meta:
        model = ServiceEvent
        fields = ['dog', 'kennel', 'event_type', 'datetime', 'location', 'duration', 'results', 'documents']
        widgets = {
            'dog': forms.Select(attrs={'class': 'form-select'}),
            'kennel': forms.Select(attrs={'class': 'form-select'}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес или описание места'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 02:00:00'}),
            'results': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'documents': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event_type'].queryset = EventType.objects.filter(is_active=True)
        self.fields['kennel'].queryset = Employee.objects.filter(is_active=True)
        self.fields['results'].required = False
        self.fields['documents'].required = False


class VeterinaryRecordForm(forms.ModelForm):
    """Форма добавления ветеринарной записи"""

    class Meta:
        model = VeterinaryRecord
        fields = ['dog', 'veterinarian', 'procedure_type', 'procedure_date',
                  'next_procedure_date', 'is_routine', 'description', 'notes']
        widgets = {
            'dog': forms.Select(attrs={'class': 'form-select'}),
            'veterinarian': forms.Select(attrs={'class': 'form-select'}),
            'procedure_type': forms.Select(attrs={'class': 'form-select'}),
            'procedure_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_procedure_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
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