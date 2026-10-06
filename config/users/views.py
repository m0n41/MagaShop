from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.contrib.auth.views import (
    LoginView, PasswordChangeView, PasswordChangeDoneView, 
    PasswordResetView, PasswordResetDoneView, 
    PasswordResetCompleteView, PasswordResetConfirmView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    LoginUserForm, RegisterUserForm, ProfileUserUpdateForm, 
    ProfileUpdateForm, UserPasswordChangeForm, UserPasswordResetForm,
    BecomeSalaryForm, BecomeSalaryComplete,
)
from .models import User, Profile
from django.contrib.auth import login, authenticate
from django.core.mail import EmailMessage
from django.conf import settings
import random
    
class RegisterUser(CreateView):
    template_name = "users/register.html"
    model = User
    form_class = RegisterUserForm
    extra_context = {"title": "Регистрация"}
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = authenticate(
            self.request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"]
        )
        if user is not None:
            login(self.request, user)
        return response
    
    def get_success_url(self):
        return reverse_lazy("catalog:product_list")
    
class LoginUser(LoginView):
    template_name = "users/login.html"
    form_class = LoginUserForm
    extra_context = {"title": "Авторизация"}
    # get_success_url не переопределён специально: LoginView сам уважает ?next=...
    # (например, редирект после LoginRequiredMixin на "Купить сейчас"), а если next
    # нет — использует LOGIN_REDIRECT_URL из settings.py.

class ProfileDetail(LoginRequiredMixin, DetailView):
    template_name = "users/profile.html"
    model = User
    context_object_name = "user_obj"
    
    def get_object(self, queryset=None):
        return self.request.user

class RecentViewsView(TemplateView):
    template_name = "users/views_list.html"
    
    def post(self, request, *args, **kwargs):
        if "recent_views" in request.session:
            del request.session["recent_views"]
        return redirect("users:views_list")

class ProfileUserUpdate(LoginRequiredMixin, UpdateView):
    template_name = "users/profile_edit.html"
    model = User
    form_class = ProfileUserUpdateForm
    extra_context = {"title": "Профиль"}
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy("users:profile")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_form"] = context["form"]
        profile = Profile.objects.get_or_create(user=self.request.user)
        context["address_form"] = ProfileUpdateForm(instance=profile[0])
        return context
    
class ProfileAddressUpdate(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = "users/profile_edit.html"
    
    def get_object(self, queryset=None):
        profile = Profile.objects.get_or_create(user=self.request.user)
        return profile[0]
    
    def get_success_url(self):
        return reverse_lazy("users:profile")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["address_form"] = context["form"]
        context["user_form"] = ProfileUserUpdateForm(instance=self.request.user)
        return context
    
class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = "users/password_change.html"
    
    def get_success_url(self):
        return reverse_lazy("users:password_change_done")

class UserPasswordChangeDone(PasswordChangeDoneView):
    template_name = "users/password_change_done.html"

class UserPasswordReset(PasswordResetView):
    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.html"
    form_class = UserPasswordResetForm
    
    def get_success_url(self):
        return reverse_lazy("users:password_reset_done")
    
class UserPasswordResetDone(PasswordResetDoneView):
    template_name = "users/password_reset_done.html"
    
class UserPasswordResetComplete(PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"

class UserPasswordResetConfirm(PasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"
    
    def get_success_url(self):
        return reverse_lazy("users:password_reset_complete")
    
class BecomeSalaryView(LoginRequiredMixin, FormView):
    template_name = "users/become_salary.html"
    form_class = BecomeSalaryForm
    
    def get_success_url(self):
        return reverse_lazy("users:become_salary_complete")
    
    def form_valid(self, form):
        code = random.randint(100000, 999999)
        self.request.session["become_salary_code"] = code
        mail = EmailMessage(
            subject="Код",
            body=f"Код {code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[form.cleaned_data["email"]],
        )
        mail.send()
        return super().form_valid(form)
    
class BecomeSalaryCompleteView(LoginRequiredMixin, FormView):
    template_name = "users/become_salary_complete.html"
    form_class = BecomeSalaryComplete
    
    def get_success_url(self):
        return reverse_lazy("users:become_salary_confirm")
    
    def form_valid(self, form):
        user_code = self.request.session.get("become_salary_code")
        if form.cleaned_data["code"] == user_code:
            if self.request.session.get("become_salary_code") is None:
                return super().form_invalid(form.add_error("code", "Неверный код"))
            user = User.objects.get(pk=self.request.user.pk)
            user.status_user = "Seller"
            user.save()
            del self.request.session["become_salary_code"]
            return super().form_valid(form)
        return super().form_invalid(form.add_error("code", "Неверный код"))

class BecomeSalaryConfirmView(LoginRequiredMixin, TemplateView):
    template_name = "users/become_salary_confirm.html"
