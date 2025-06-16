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
