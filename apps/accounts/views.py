"""Accounts app views"""
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import User


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("articles:home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Welcome, {user.username}! Your account has been created.")
        return redirect(self.success_url)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("articles:home")
        return super().dispatch(request, *args, **kwargs)


class LoginView(CreateView):
    template_name = "accounts/login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("articles:home")
        form = LoginForm()
        return render(request, self.template_name, {"form": form, "next": request.GET.get("next", "")})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request, data=request.POST)
        next_url = request.POST.get("next") or request.GET.get("next") or "articles:home"
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(next_url)
        return render(request, self.template_name, {"form": form, "next": next_url})


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/profile.html"
    context_object_name = "profile_user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        ctx["articles"] = profile_user.articles.filter(status="published").order_by("-published_at")[:6]
        return ctx


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileUpdateForm
    template_name = "accounts/profile_update.html"

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy("accounts:profile", kwargs={"username": self.request.user.username})

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("articles:home")

