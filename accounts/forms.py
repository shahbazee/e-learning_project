from django import forms


class SignupForm(forms.Form):
    username = forms.CharField(initial="shahbaz")
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput())