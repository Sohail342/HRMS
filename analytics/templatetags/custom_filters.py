from django import template

register = template.Library()

@register.filter
def percentage_of(value, total):
    """
    Calculate what percentage of total is value
    """
    try:
        if total == 0:
            return 0
        return int((float(value) / float(total)) * 100)
    except (ValueError, ZeroDivisionError):
        return 0