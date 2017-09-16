from django.contrib.auth.models import User
from django import forms
from .models import *

genders = (

			('M', 'MALE'),
			('F', 'FEMALE'),
		)

class UserForm(forms.ModelForm):
	
	class Meta:
		model = User
		fields = ('username', 'password')
		widgets = {
            'username':forms.TextInput(attrs={'placeholder':'Username'}),
            'password': forms.PasswordInput(attrs={'placeholder':'Password'}), 
        }

class ParticipantForm(forms.ModelForm):
	
	phone = forms.RegexField(regex=r'^\d{10}$')

	class Meta:
		model = Participant
		fields = ('email', 'city', 'name', 'college', 'state', 'phone', 'gender',)