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

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists. Please login instead."
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
    username_or_email = forms.CharField(
        label="Username or Email",
        max_length=254
    )
    password = forms.CharField(
        widget=forms.PasswordInput()
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Email Address")


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        label="New Password",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        label="Confirm Password",
    )

    def clean_new_password(self):
        password = self.cleaned_data["new_password"]

        if len(password) < 8:
            raise forms.ValidationError(
                "Password must be at least 8 characters."
            )

        return password

    def clean(self):
        cleaned_data = super().clean()

        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data


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

    def clean_email(self):
        email = self.cleaned_data["email"]
        duplicate = (
            User.objects.filter(email__iexact=email)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if duplicate:
            raise forms.ValidationError(
                "This email address is already in use by another account."
            )
        return email

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput()
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput()
    )
