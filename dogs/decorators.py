# Декоратор — это обёртка над функцией (view).
# Проверяет роль пользователя перед тем как пустить его на страницу.

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*role_names):
    """
    Использование:
        @role_required('Кинолог', 'Руководитель')
        def my_view(request):
            ...
    Пускает на страницу только пользователей с указанными ролями.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # Если пользователь не вошёл — на страницу входа
            if not request.user.is_authenticated:
                return redirect('login')

            # Суперпользователь (администратор) проходит всегда
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Проверяем есть ли у пользователя нужная роль
            try:
                employee = request.user.employee  # связанный сотрудник
                user_roles = employee.roles.values_list('name', flat=True)
                if any(role in user_roles for role in role_names):
                    return view_func(request, *args, **kwargs)
            except Exception:
                pass

            # Роли нет — показываем ошибку и возвращаем на дашборд
            messages.error(request, 'У вас нет доступа к этому разделу.')
            return redirect('dashboard')

        return wrapper
    return decorator


def get_user_roles(user):
    """Возвращает список ролей пользователя. Удобно использовать в шаблонах."""
    if not user.is_authenticated:
        return []
    if user.is_superuser:
        return ['Администратор', 'Руководитель', 'Кинолог', 'Ветеринар']
    try:
        return list(user.employee.roles.values_list('name', flat=True))
    except Exception:
        return []