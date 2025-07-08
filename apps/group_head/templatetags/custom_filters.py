from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)



@register.filter
def capitalize_words(value):
    # Capitalize the first letter of each word
    if value is None:
        return ''
    return ' '.join([word.capitalize() for word in value.split()])


@register.filter
def add_pdf(url:str):
    if not url.endswith('.pdf'):
        return f'{url}.pdf'
    return url



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
