from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login as auth_login
from django.core.mail import send_mail

from .forms import SignupForm, LoginForm, ProfileUpdateForm
from .models import EmailOTP

import random


# Create your views here.


@login_required
def profile(request):
    user = request.user
    return render(request, "accounts/profile.html", {"user": user})


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
                    "otp": otp
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

        # Check OTP
        if entered_otp == otp_object.otp:

            # Activate account
            user.is_active = True
            user.save()

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

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

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
                "Invalid username or password."
            )

    else:
        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {"form": form}
    )


@login_required
def edit_profile(request):

    user = request.user

    if request.method == "POST":

        form = ProfileUpdateForm(request.POST)

        if form.is_valid():

            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]

            user.save()

            return redirect("profile")

    else:

        form = ProfileUpdateForm(
            initial={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {"form": form}
    )

