from datetime import date, timedelta
from django.forms import Form, CharField, TextInput, EmailField, ImageField, ValidationError, DateField
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

from phonenumber_field.formfields import PhoneNumberField
from django_recaptcha.fields import ReCaptchaField
from users.models import User
from app.settings import MIN_USER_AGE

User = get_user_model()


class UserLoginForm(AuthenticationForm):
    username = CharField()
    password = CharField()
    captcha = ReCaptchaField()


class UserRegisterForm(UserCreationForm):
    first_name = CharField()
    last_name = CharField(required=False)
    username = CharField()
    email = EmailField()
    password1 = CharField()
    password2 = CharField()
    captcha = ReCaptchaField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2',
            'captcha'
        )


class UserProfileForm(UserChangeForm):
    avatar_image = ImageField(required=False)
    first_name = CharField()
    last_name = CharField(required=False)
    username = CharField()
    email = EmailField(disabled=True)
    phone_number = PhoneNumberField(region='UA', required=False)
    birthday_date = DateField(required=False)
    description = TextInput()

    class Meta:
        model = User
        fields = (
            'avatar',
            'first_name',
            'last_name',
            'username',
            'email',
            'phone_number',
            'birthday_date',
            'description',
        )

    def clean_birthday_date(self):
        birthday_date: date = self.cleaned_data['birthday_date']

        if birthday_date:
            if birthday_date > date.today():
                raise ValidationError(
                    'Дата народження не може бути у майбутньому')
            if date.today() - timedelta(days=365*MIN_USER_AGE) < birthday_date:
                raise ValidationError(
                    f'Вам повинно бути не менше {MIN_USER_AGE} років')
        return birthday_date


class ResetTokenForm(Form):
    token = CharField()
    captcha = ReCaptchaField()


class ResetPasswordForm(Form):
    email = EmailField()
    captcha = ReCaptchaField()


class SetNewPasswordForm(Form):
    password1 = CharField()
    password2 = CharField()
    captcha = ReCaptchaField()

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        try:
            validate_password(password1)
        except ValidationError as er:
            self.add_error('password1', er)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data['password1']
        password2 = cleaned_data['password2']

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Паролі не співпадають')

        return cleaned_data
