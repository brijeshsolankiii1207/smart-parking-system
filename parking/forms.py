from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'})
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username", "password1", "password2"]


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your registered email', 'class': 'form-control'})
    )
