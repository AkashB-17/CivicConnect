from django import template

register = template.Library()

@register.filter
def status_color(status_name):
    color_map = {
        'submitted': 'secondary',
        'in_review': 'warning',
        'in_progress': 'info',
        'resolved': 'success',
        'rejected': 'danger',
    }
    return color_map.get(status_name, 'secondary')

@register.filter
def priority_color(priority):
    color_map = {
        'low': 'success',
        'medium': 'warning',
        'high': 'danger',
        'urgent': 'danger',
    }
    return color_map.get(priority, 'secondary') 