from django import forms
from django.template import Library

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=255, 
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your username',
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Password'
    )

# Template filter to add custom classes to form fields
register = Library()

@register.filter(name='add_class')
def add_class(value, arg):
    css_classes = value.field.widget.attrs.get('class', '')
    if css_classes:
        css_classes = f"{css_classes} {arg}"
    else:
        css_classes = arg
    return value.as_widget(attrs={'class': css_classes})