"""
Custom template tags and filters for permission checking
"""
from django import template

register = template.Library()


@register.filter(name='has_perm')
def has_perm(user, permission_name):
    """
    Template filter to check if user has a specific permission

    Usage in template:
    {% if user|has_perm:"จัดการผู้ใช้งาน" %}

    Args:
        user: User object
        permission_name: Permission name string

    Returns:
        Boolean
    """
    if not user or not user.is_authenticated:
        return False

    # Use the has_permission method from User model
    return user.has_permission(permission_name)


@register.filter(name='has_any_perm')
def has_any_perm(user, permission_names):
    """
    Check if user has any of the specified permissions

    Usage:
    {% if user|has_any_perm:"perm1,perm2,perm3" %}

    Args:
        user: User object
        permission_names: Comma-separated permission names

    Returns:
        Boolean
    """
    if not user or not user.is_authenticated:
        return False

    perms = [p.strip() for p in permission_names.split(',')]
    return any(user.has_permission(perm) for perm in perms)
