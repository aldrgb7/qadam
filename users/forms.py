from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

# --- ТВОИ СТАРЫЕ ФОРМЫ (РЕГИСТРАЦИЯ И ВХОД) ---

class CustomUserCreationForm(forms.ModelForm):
    # Добавляем поле роли, которое будет скрыто (мы будем управлять им через JS и наши карточки)
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.HiddenInput(),
        initial='student'
    )
    
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Придумайте сложный пароль', 'class': 'form-control'}),
        help_text="Минимум 8 символов."
    )

    class Meta:
        model = CustomUser
        # Добавили 'role' в fields
        fields = ('role', 'username', 'email', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class EmailVerificationForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control-code', 'placeholder': '000000'}),
        max_length=6,
        label="Код подтверждения"
    )

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин или Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))


# --- НОВАЯ ФОРМА ДЛЯ ПРОФИЛЯ (ДОБАВЬ ЭТО) ---

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Логин'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Фамилия'}),
            'avatar': forms.FileInput(attrs={'class': 'file-input'}),
        }