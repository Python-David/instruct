from django import forms

from .models import Account


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter Password",
            }
        )
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm Password", "class": ""}
        )
    )

    class Meta:
        model = Account
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "password",
        ]

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        field_names_and_placeholders = {
            "first_name": "Enter First Name",
            "last_name": "Enter Last Name",
            "phone_number": "Enter Phone Number",
            "email": "Enter Email",
            "password": "Enter Password",
            "confirm_password": "Cofirm Password",
        }

        field_ids = {
            "first_name": "typeFirstNameX",
            "last_name": "typeLastNameX",
            "email": "typeEmailX",
            "phone_number": "typePhoneNumberX",
            "password": "typePasswordX",
            "confirm_password": "typeConfirmPasswordX",
        }

        for field_name, placeholder in field_names_and_placeholders.items():
            self.fields[field_name].widget.attrs.update({
                "placeholder": placeholder,
                "class": "form-control form-control-lg",
                "id": field_ids[field_name],
            })


    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do no match!")
