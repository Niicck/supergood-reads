from django.urls import path

from tests.sample_app.basic_auth.views import (
    BasicLoginView,
    BasicLogoutView,
    BasicPasswordChangeView,
    BasicSignUpView,
)

urlpatterns = [
    path("login/", BasicLoginView.as_view(), name="login"),
    path("logout/", BasicLogoutView.as_view(), name="logout"),
    path("password_change/", BasicPasswordChangeView.as_view(), name="password_change"),
    path("sign-up/", BasicSignUpView.as_view(), name="sign_up"),
]
