from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)



@register.filter
def capitalize_words(value):
    # Capitalize the first letter of each word
    return ' '.join([word.capitalize() for word in value.split()])
