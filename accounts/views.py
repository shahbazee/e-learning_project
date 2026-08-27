from django.shortcuts import render
from .forms import SignupForm
# Create your views here.

def profile(request):
    return render(request, "accounts/profile.html")

def signup(request):
    form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})



