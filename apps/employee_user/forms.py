# HRIS_App/forms.py
from django import forms
from django.contrib.auth.hashers import make_password  # To hash the password
from apps.HRIS_App.models import Employee

class CreatePasswordForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('password', 'email' )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Hash the password before saving it
            return make_password(password)
        return password
