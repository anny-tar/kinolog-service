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
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            try:
                employee = request.user.employee
                user_roles = list(employee.roles.values_list('name', flat=True))
                # print("=== DECORATOR DEBUG ===")
                # print("User:", request.user.username)
                # print("Roles in DB:", user_roles)
                # print("Required roles:", role_names)
                # print("Match:", any(role in user_roles for role in role_names))
                if any(role in user_roles for role in role_names):
                    return view_func(request, *args, **kwargs)
            except Exception as e:
                print("EXCEPTION:", e)

            messages.error(request, 'У вас нет доступа к этому разделу.')
            return redirect('login')

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