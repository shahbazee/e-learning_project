from django import forms


class SignupForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())


    def clean_username(self):
        username = self.cleaned_data["username"]

        if "@" in username:
            raise forms.ValidationError(
                "Username cannot contain@."
            )
        return username


    
    def clean_email(self):
        email = self.cleaned_data["email"]

        if not email.endswith("@gmail.com"):
            raise forms.ValidationError(
                "Email must be a Gmail Address. "
            )
        return email


    
    def clean_password(self):
        password = self.cleaned_data["password"]

        if len(password) < 8:
            raise forms.ValidationError(
                "Password must be at least 8 characters."
            )
        return password


class LoginForm(forms.Form):
    username= forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())



class SearchForm(forms.Form):
    search = forms.CharField()


    def cleaned_search(self):
        search = self.cleaned_data["search"]

        if len(search) < 10:
            raise forms.ValidationError(
                "Search characters must be the 10. "
            )
        return search
    

class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()



class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_pasword = forms.CharField(widget=forms.PasswordInput())




