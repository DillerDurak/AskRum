from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import *
from snowpenguin.django.recaptcha3.widgets import ReCaptchaHiddenInput
# from captcha.fields import CaptchaField


class MyUserCreationForm(UserCreationForm):
    captcha = ReCaptchaHiddenInput()
    email = forms.EmailField(help_text='You should enter your own email. If you forgot your password, you would change it through your email.')
    username = forms.CharField(max_length=16, label='Username (maximum 16 symbols)')

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput)
    password = forms.CharField(label='Password',widget=forms.PasswordInput)


class RoomCreationForm(forms.ModelForm):
    image = forms.ImageField(required=False, widget=forms.FileInput)

    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants', 'topic']


class UserForm(forms.ModelForm):
    avatar = forms.ImageField(required=False, widget=forms.FileInput)

    class Meta:
        model = User
        fields = ['name', 'email', 'avatar','bio']


class PasswordConfirmation(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'off'}), label='Password Confirmation')

    class Meta:
        model = User
        fields = ['password']





