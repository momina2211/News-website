"""Accounts app forms"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={"class": "form-input", "placeholder": "your@email.com"}
    ))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={"class": "form-input", "placeholder": "First name"}
    ))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={"class": "form-input", "placeholder": "Last name"}
    ))

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-input", "placeholder": "Username", "autofocus": True}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "form-input", "placeholder": "Password"}
    ))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "bio", "avatar", "website", "twitter")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "class": "form-textarea"}),
            "website": forms.URLInput(attrs={"class": "form-input"}),
            "twitter": forms.TextInput(attrs={"class": "form-input", "placeholder": "@handle"}),
        }

