from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """
    Multiplies two values and returns the result.
    If either value is not a valid number, it returns 0.
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0  # Default to 0 in case of errors

@register.filter
def get_item(dictionary, key):
    """
    Retrieves a value from a dictionary given a key.
    """
    try:
        return dictionary.get(key, '')
    except AttributeError:
        return ''  # Return an empty string if the input is not a dictionary


@register.filter
def get_item(dictionary, key):
  if isinstance(dictionary, dict):
    return dictionary.get(key,  '')
  elif hasattr(dictionary, 'items'):  # Check if it's a dict_items object
    try:
      return dict(dictionary)[key]
    except KeyError:
      return ''
  else:
    return ''