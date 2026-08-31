from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login as auth_login
from .forms import SignupForm, LoginForm, ProfileUpdateForm
# Create your views here.


@login_required
def profile(request):
    user = request.user
    return render(request, "accounts/profile.html", {"user": user})

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            User.objects.create_user(
                username= form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"]
            )

            return redirect("login")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})

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

    return render(request, "accounts/edit_profile.html", {"form": form})
