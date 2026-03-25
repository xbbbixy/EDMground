from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        label="用户名",
        help_text="必填，150 个字符以内，可包含字母、数字和 @ / . + - _",
        widget=forms.TextInput(attrs={
            'placeholder': '用户名'
        })
    )

    email = forms.EmailField(
        label="邮箱地址",
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': '邮箱'
        })
    )

    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={
            'placeholder': '密码'
        }),
        help_text="密码不少于 8 位，不能过于简单"
    )

    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(attrs={
            'placeholder': '确认密码'
        }),
        help_text="请再次输入密码"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("两次密码不一致！")
        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={
            'placeholder': '用户名'
        }))
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={
            'placeholder': '密码'
        }))
