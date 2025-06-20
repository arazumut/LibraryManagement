from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to a form field widget."""
    if hasattr(field, 'as_widget'):
        attrs = {'class': f"{field.field.widget.attrs.get('class', '')} {css_class}".strip()}
        return field.as_widget(attrs=attrs)
    return field

@register.filter(name='attr')
def set_attr(field, attr_args):
    """
    Set HTML attributes for a form field widget.
    Usage: {{ field|attr:"rows:5" }}
    """
    if not hasattr(field, 'field'):
        return field
    
    args = attr_args.split(':')
    if len(args) == 2:
        attr, value = args
        field.field.widget.attrs[attr] = value
    return field
