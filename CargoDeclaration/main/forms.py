from django import forms
from .models import AdvUser
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .apps import user_registered
from django.forms import inlineformset_factory
from .models import DeclarationLog, CargoReceiver, Consignor, Summary


class ChangeInfoFormUser(forms.ModelForm):
    email = forms.EmailField(required=True, label='Электронная почта')

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'send_messages', 'job_title', 'phone_number')


class RegisterFormUser(forms.ModelForm):
    email = forms.EmailField(required=True, label='Электронная почта')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Повторно пароль', widget=forms.PasswordInput,
                                help_text='Введите пароль повторно')

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Ошибка. Введеные пароли разные!', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registered.send(RegisterFormUser, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name',
                  'last_name', 'send_messages', 'job_title', 'phone_number')


class DeclarationForm(forms.ModelForm):
    """Класс - форма для создания декларации на груз"""

    class Meta:
        model = DeclarationLog
        fields = '__all__'
        exclude = ('status',)
        # widgets = {'user_id': forms.HiddenInput,'cargo_id': forms.HiddenInput}


#
#

AIFormSet = inlineformset_factory(DeclarationLog, CargoReceiver, fields='__all__')


class CargoReceiverForm(forms.ModelForm):
    """Класс - форма для добавления в декларацию сведений о получателе"""

    class Meta:
        model = CargoReceiver
        fields = '__all__'
        exclude = ('id',)


class ConsignorForm(forms.ModelForm):
    """Класс - форма для добавления в декларацию сведений об отправителе"""

    class Meta:
        model = Consignor
        fields = '__all__'
        exclude = ('id',)
        # widgets = {'id': forms.HiddenInput}


class SummmaryForm(forms.ModelForm):
    """Класс - форма для добавления сводок о декларациях"""

    class Meta:
        model = Summary
        fields = '__all__'
        exclude = ('id',)
