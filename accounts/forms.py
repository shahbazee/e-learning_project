from django import forms
from django.contrib.auth.models import User

class SignupForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean_username(self):
        username = self.cleaned_data["username"]

        if "@" in username:
            raise forms.ValidationError(
                "Username cannot contain @."
            )   

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if not email.endswith("@gmail.com"):
            raise forms.ValidationError(
                "Sign up with Google Account."
            )

        return email

    def clean_password(self):
        password = self.cleaned_data["password"]

        if len(password) < 8:
            raise forms.ValidationError(
                "Password must be at least 8 characters."
            )

        return password

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(
        widget=forms.PasswordInput()
    )


class SearchForm(forms.Form):
    search = forms.CharField()

    def clean_search(self):
        search = self.cleaned_data["search"]

        if len(search) < 10:
            raise forms.ValidationError(
                "Search must contain at least 10 characters."
            )

        return search


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput()
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput()
    )
