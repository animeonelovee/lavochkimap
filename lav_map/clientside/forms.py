from django import forms
from django.contrib.auth.forms import (UserCreationForm as DjangoUserCreationForm, AuthenticationForm as DjangoAuthenticationForm)
from django.contrib.auth import get_user_model, authenticate
from .utils import send_email_for_verify
from django.core.exceptions import ValidationError
from .models import Lavochki, RatingStar, Marks, PhotoLav

CHOICES = [
    (1, ''),
    (2, ''),
    (3, ''),
    (4, ''),
    (5, ''),
]

User = get_user_model()

class AuthenticationForm(DjangoAuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

            if not self.user_cache.email_verify:
                send_email_for_verify(self.request, self.user_cache)
                raise ValidationError(
                    'Почта не верифицирована. Проверьте вашу почту.',
                    code='invalid_login',
                )
        
        return self.cleaned_data    

class UserCreationForm(DjangoUserCreationForm):
    email = forms.EmailField(
        label = ("Email"),
        max_length = 254,
        widget = forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

class AddLavochkaForm(forms.ModelForm):
    '''
    rating = forms.ModelChoiceField(
        queryset = RatingStar.objects.all(),
        widget = forms.RadioSelect(),
        empty_label = None
    )

    image_path = forms.ImageField(
        label = ("Загрузите фото (не более 6)"),
        widget = forms.FileInput(attrs={'multiple': 'multiple'}),
    )
    '''

    class Meta:
        model = Lavochki
        fields = ['x', 'y', 'description', 'is_padik', 'is_spinka', 'is_ten']
        widgets = {
            'x':forms.NumberInput(attrs={'class': "form-control"}),
            'y':forms.NumberInput(attrs={'class': "form-control"}),
            'description':forms.Textarea(attrs={'class': "form-control"}),
            'is_padik':forms.NullBooleanSelect(attrs={'class': 'form-select'}),
            'is_spinka':forms.NullBooleanSelect(attrs={'class': 'form-select'}),
            'is_ten':forms.NullBooleanSelect(attrs={'class': 'form-select'}),
        }

class AddProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'photo']
        widgets = {
            'photo':forms.FileInput(),
        }

class AddMarksForm(forms.ModelForm):

    rating = forms.ModelChoiceField(
        queryset = RatingStar.objects.all(),
        widget = forms.RadioSelect(),
        empty_label = None,
    )

    class Meta:
        model = Marks
        fields = ['rating']

class AddPhotoForm(forms.ModelForm):

    image_path = forms.ImageField(
        label = ("Загрузите фото (не более 6)"),
        widget = forms.FileInput(attrs={'multiple': 'multiple'}),
    )

    class Meta:
        model = PhotoLav
        fields = ['image_path']


        

