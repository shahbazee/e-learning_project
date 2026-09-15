from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("login/", views.login, name="login"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("verify-reset-otp/", views.verify_reset_otp, name="verify_reset_otp"),
    path("reset-password/", views.reset_password, name="reset_password")
]
