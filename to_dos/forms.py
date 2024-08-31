from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from collections import OrderedDict


class MyUserCreationForm(UserCreationForm):

    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True, label="First name")

    class Meta:
        model = User
        fields = ("first_name", "email", "password1", "password2")

    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists")
        return email


    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]

        user.username = self.cleaned_data["email"]

        if commit:
            user.save()
        return user
    
class MyAuthenticationForm(AuthenticationForm):

    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ["email", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.pop('username', None)
        self.fields = OrderedDict([
            ('email', self.fields['email']),
            ('password', self.fields['password']),
        ])

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:

            try:
                user = User.objects.get(email=email)
                self.user_cache = authenticate(username=user.username, password=password)
                if self.user_cache is None:
                    raise ValidationError("Invalid credentials")
            except User.DoesNotExist:
                raise ValidationError("A user with this email does not exist")
            
        return self.cleaned_data
