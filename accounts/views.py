from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login as auth_login
from django.core.mail import send_mail
from django.utils import timezone

from datetime import timedelta

from elearning_site.emails import (
    send_password_reset_confirmation_email,
    send_welcome_email,
)

from .forms import (
    SignupForm,
    LoginForm,
    ProfileUpdateForm,
    ForgotPasswordForm,
    PasswordResetForm,
)
from .models import EmailOTP, OTP_EXPIRY_MINUTES
from enrollments.models import Enrollment

import random


# Create your views here.


@login_required
def profile(request):
    user = request.user

    enrollments = Enrollment.objects.filter(
        user=user
    ).select_related("course")

    enrolled_count = enrollments.count()
    completed_count = enrollments.filter(progress__gte=100).count()
    in_progress_count = enrolled_count - completed_count

    # First character of the user's name for the avatar
    initial = (user.first_name or user.username)[:1].upper()

    return render(
        request,
        "accounts/profile.html",
        {
            "user": user,
            "enrollments": enrollments,
            "enrolled_count": enrolled_count,
            "completed_count": completed_count,
            "in_progress_count": in_progress_count,
            "initial": initial,
        },
    )


def signup(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            # Create user without activating the account
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"]
            )

            # User cannot login until email is verified
            user.is_active = False
            user.save()

            # Generate 6-digit OTP
            otp = str(random.randint(100000, 999999))

            # Save OTP for this user
            EmailOTP.objects.update_or_create(
                user=user,
                defaults={
                    "otp": otp,
                    "purpose": EmailOTP.PURPOSE_SIGNUP,
                    "expires_at": timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
                }
            )

            # Send OTP to user's email
            send_mail(
                "E-Learning Email Verification",
                f"Your OTP is: {otp}",
                None,
                [user.email],
                fail_silently=False,
            )

            # Store user ID in session
            request.session["otp_user_id"] = user.id

            # Go to OTP verification page
            return redirect("verify_otp")

    else:
        form = SignupForm()

    return render(
        request,
        "accounts/signup.html",
        {"form": form}
    )


def verify_otp(request):

    # Get user ID from session
    user_id = request.session.get("otp_user_id")

    if not user_id:
        return redirect("signup")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        try:
            otp_object = EmailOTP.objects.get(user=user)

        except EmailOTP.DoesNotExist:

            return render(
                request,
                "accounts/verify_otp.html",
                {
                    "error": "OTP not found."
                }
            )

        if otp_object.is_expired():
            return render(
                request,
                "accounts/verify_otp.html",
                {
                    "error": "This OTP has expired. Please sign up again to receive a new verification code."
                }
            )

        # Check OTP
        if entered_otp == otp_object.otp:

            # Activate account
            user.is_active = True
            user.save()

            # Send confirmation email after successful registration
            send_welcome_email(user)

            # Delete OTP after successful verification
            otp_object.delete()

            # Remove user ID from session
            request.session.pop("otp_user_id", None)

            # Go to login
            return redirect("login")

        else:

            return render(
                request,
                "accounts/verify_otp.html",
                {
                    "error": "Invalid OTP."
                }
            )

    return render(
        request,
        "accounts/verify_otp.html"
    )


def logout_view(request):
    logout(request)
    return redirect("login")


def login(request):

    if request.method == "POST":

        form = LoginForm(request.POST)

        if form.is_valid():

            username_or_email = form.cleaned_data["username_or_email"]
            password = form.cleaned_data["password"]

            # Check if input is email or username
            user = None
            
            if "@" in username_or_email:
                # It's an email, look up user by email
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    username = user_obj.username
                except User.DoesNotExist:
                    username = None
            else:
                # It's a username
                username = username_or_email

            # Try to authenticate
            if username:
                user = authenticate(
                    request,
                    username=username,
                    password=password
                )

            if user is not None:

                auth_login(request, user)

                return redirect("home")

            form.add_error(
                None,
                "Invalid username/email or password."
            )

    else:
        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {"form": form}
    )


def forgot_password(request):

    if request.method == "POST":

        form = ForgotPasswordForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(email=email)

            except User.DoesNotExist:
                user = None

            if user is not None:

                # Generate 6-digit OTP
                otp = str(random.randint(100000, 999999))

                # Save OTP for password reset
                EmailOTP.objects.update_or_create(
                    user=user,
                    defaults={
                        "otp": otp,
                        "purpose": EmailOTP.PURPOSE_RESET,
                        "expires_at": timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
                    }
                )

                # Send OTP to user's email
                send_mail(
                    "E-Learning Password Reset",
                    f"""Hello {user.username},

We received a request to reset your password.

Your password reset OTP is: {otp}

If you did not request this, you can ignore this email.

Best regards,
E-Learning Team""",
                    None,
                    [user.email],
                    fail_silently=False,
                )

                # Store user ID in session
                request.session["reset_user_id"] = user.id

                # Go to OTP verification page
                return redirect("verify_reset_otp")

            # Do not reveal whether the email exists
            return render(
                request,
                "accounts/forgot_password.html",
                {
                    "form": form,
                    "message": (
                        "If an account exists with that email, "
                        "a password reset OTP has been sent."
                    ),
                },
            )

    else:
        form = ForgotPasswordForm()

    return render(
        request,
        "accounts/forgot_password.html",
        {"form": form}
    )


def verify_reset_otp(request):

    # Get user ID from session
    user_id = request.session.get("reset_user_id")

    if not user_id:
        return redirect("forgot_password")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        try:
            otp_object = EmailOTP.objects.get(user=user)

        except EmailOTP.DoesNotExist:

            return render(
                request,
                "accounts/verify_reset_otp.html",
                {
                    "error": "OTP not found."
                }
            )

        if otp_object.is_expired():
            return render(
                request,
                "accounts/verify_reset_otp.html",
                {
                    "error": "This OTP has expired. Please request a new reset link."
                }
            )

        if (
            otp_object.purpose == EmailOTP.PURPOSE_RESET
            and entered_otp == otp_object.otp
        ):

            # Mark OTP as verified
            request.session["reset_otp_verified"] = True

            # Go to reset password page
            return redirect("reset_password")

        return render(
            request,
            "accounts/verify_reset_otp.html",
            {
                "error": "Invalid OTP."
            }
        )

    return render(
        request,
        "accounts/verify_reset_otp.html"
    )


def reset_password(request):

    # Get user ID from session
    user_id = request.session.get("reset_user_id")
    verified = request.session.get("reset_otp_verified", False)

    if not user_id or not verified:
        return redirect("forgot_password")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":

        form = PasswordResetForm(request.POST)

        if form.is_valid():

            new_password = form.cleaned_data["new_password"]

            # Set the new password
            user.set_password(new_password)
            user.save()

            # Send a confirmation email after a successful reset
            send_password_reset_confirmation_email(user)

            # Delete the reset OTP
            EmailOTP.objects.filter(
                user=user,
                purpose=EmailOTP.PURPOSE_RESET,
            ).delete()

            # Clear session data
            request.session.pop("reset_user_id", None)
            request.session.pop("reset_otp_verified", None)

            # Go to login with success message
            return render(
                request,
                "accounts/login.html",
                {
                    "form": LoginForm(),
                    "message": (
                        "Your password has been reset successfully. "
                        "Please log in with your new password."
                    ),
                },
            )

    else:
        form = PasswordResetForm()

    return render(
        request,
        "accounts/reset_password.html",
        {"form": form}
    )


@login_required
def edit_profile(request):

    user = request.user

    if request.method == "POST":

        # Pass the current user as the instance so the ModelForm validates
        # against the existing record (e.g. keeping your own email must not
        # be treated as a duplicate) and saves directly to that user.
        form = ProfileUpdateForm(request.POST, instance=user)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your profile has been updated successfully."
            )

            return redirect("profile")

    else:

        form = ProfileUpdateForm(instance=user)

    return render(
        request,
        "accounts/edit_profile.html",
        {"form": form}
    )

