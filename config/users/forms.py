from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, PasswordResetForm
from django import forms
from django.contrib.auth import get_user_model
from .models import User, Profile

class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={"class": "form-input"}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-input"}))
    password1 = forms.CharField(label="Пароль", strip=False, widget=forms.PasswordInput(attrs={"class": "form-input"}))
    password2 = forms.CharField(label="Подтверждение пароля", strip=False, widget=forms.PasswordInput(attrs={"class": "form-input"}))
    
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password1", "password2"]

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label="Логин или email", widget=forms.TextInput(attrs={"class": "form-input"}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-input"}))
    
    class Meta:
        model = get_user_model()
        fields = ["username", "password"]

class ProfileUserUpdateForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label="Логин", widget=forms.TextInput(attrs={"class": "form-input"}))
    email = forms.CharField(disabled=True, label="E-mail", widget=forms.TextInput(attrs={"class": "form-input"}))
    
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "first_name", "last_name", "photo"]
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input"}),
            "last_name": forms.TextInput(attrs={"class": "form-input"}),
        }
        
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "address", "city"]
        labels = {
            "phone": "Телефон",
            "address": "Адрес",
            "city": "Город",
        }
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-input"}),
            "address": forms.TextInput(attrs={"class": "form-input"}),
            "city": forms.TextInput(attrs={"class": "form-input"})
        }

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", strip=False, widget=forms.PasswordInput(attrs={"class": "form-input"}))
    new_password1 = forms.CharField(label="Новый пароль", strip=False, widget=forms.PasswordInput(attrs={"class": "form-input"}))
    new_password2 = forms.CharField(label="Подтверждение пароля", strip=False, widget=forms.PasswordInput(attrs={"class": "form-input"}))

class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={"class": "form-input"}))

class BecomeSalaryForm(forms.Form):
    email = forms.CharField(label="E-mail", widget=forms.TextInput(attrs={"class": "form-input"}))
    
class BecomeSalaryComplete(forms.Form):
    code = forms.IntegerField(label="Код", widget=forms.TextInput(attrs={"class": "form-input"}))