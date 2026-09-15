from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Contact-us form. Stored in the DB and emailed to the admin."""

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Enter your email"}),
            "subject": forms.TextInput(attrs={"placeholder": "Enter subject"}),
            "message": forms.Textarea(
                attrs={"placeholder": "Write your message", "rows": 6}
            ),
        }