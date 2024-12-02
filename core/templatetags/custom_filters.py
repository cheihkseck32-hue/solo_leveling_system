from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def difficulty_color(value):
    colors = {
        1: 'success',   # Easy
        2: 'info',      # Medium
        3: 'warning',   # Hard
        4: 'danger',    # Expert
        5: 'dark'       # Legendary
    }
    return colors.get(value, 'secondary')

@register.filter
def status_color(value):
    colors = {
        'not_started': 'secondary',
        'in_progress': 'primary',
        'completed': 'success',
        'failed': 'danger'
    }
    return colors.get(value, 'secondary')
