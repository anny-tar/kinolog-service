from .decorators import get_user_roles


def user_roles(request):
    """
    Добавляет переменную user_roles в контекст каждого шаблона.
    Благодаря этому не нужно передавать роли в каждом view вручную.
    """
    return {'user_roles': get_user_roles(request.user)}