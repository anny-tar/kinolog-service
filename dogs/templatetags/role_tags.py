from django import template
from dogs.decorators import get_user_roles

register = template.Library()


@register.filter
def has_role(user_roles, roles_string):
    """
    Шаблонный фильтр: проверяет есть ли у пользователя одна из ролей.
    Использование в шаблоне: {{ user_roles|has_role:"Кинолог,Руководитель" }}
    """
    required = [r.strip() for r in roles_string.split(',')]
    return any(role in user_roles for role in required)


@register.simple_tag(takes_context=True)
def get_roles(context):
    """Тег для получения ролей в шаблоне: {% get_roles as user_roles %}"""
    request = context.get('request')
    if request:
        return get_user_roles(request.user)
    return []