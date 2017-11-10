from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required')
    #first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    #last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    phone_no = forms.CharField(max_length=20, required=False, help_text='Required')
    choices=[('student','student'),('tutor','tutor'),('both','both')]
    user_type = forms.ChoiceField(choices=choices, widget=forms.RadioSelect())
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2','phone_no','user_type' )
        #fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2','phone_no','user_type' )