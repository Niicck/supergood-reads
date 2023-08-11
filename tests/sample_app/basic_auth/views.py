import logging
from typing import Any

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

logger = logging.getLogger(__name__)


class AuthMixin:
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)  # type: ignore


class BasicLoginView(AuthMixin, LoginView):
    template_name = "sample_app/basic_auth/login.html"

    def form_valid(self, form: AuthenticationForm) -> Any:
        response = super().form_valid(form)
        messages.success(self.request, f"Welcome, {self.request.user.username}!")
        return response


class BasicLogoutView(LogoutView):
    next_page = reverse_lazy("home")


class BasicPasswordChangeView(PasswordChangeView):
    template_name = "sample_app/basic_auth/password_change.html"
    success_url = reverse_lazy("reviews")  # TODO: redirect to profile


class BasicSignUpView(AuthMixin, CreateView[User, UserCreationForm[User]]):
    template_name = "sample_app/basic_auth/sign_up.html"
    success_url = reverse_lazy("reviews")
    form_class = UserCreationForm[User]
    object: User

    @transaction.atomic
    def form_valid(self, form: UserCreationForm[User]) -> Any:
        response = super().form_valid(form)

        # Add new user to "Reviewer" group
        group = Group.objects.filter(name="supergood_reads.Reviewer").first()
        if group:
            self.object.groups.add(group)
        else:
            logger.warning(
                f"Reviewer group DoesNotExist. User {self.object.id} was not added to it. Did you run create_groups management command?"
            )

        # Log them in
        login(self.request, self.object)

        messages.success(self.request, f"Welcome, {self.object.username}!")

        return response
