from django.contrib.auth.models import User
from django import forms
from .models import *

gender = (

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

class GroupLeaderForm(forms.ModelForm):
	
	phone = forms.RegexField(regex=r'^\d{10}$')

	class Meta:
		model = GroupLeader
		fields = ('email', 'city', 'name', 'college', 'state', 'phone', 'gender',)

		widgets = {
		'email':forms.TextInput(attrs={'placeholder':'Email',}),
		'gender':forms.Select(choices = gender),
		'name':forms.TextInput(attrs={'placeholder':'FullName'})
		}

class TeamCaptainForm(forms.ModelForm):
	phone = forms.RegexField(regex=r'^\d{10}$')

	class Meta:
		model = Captain

		fields = ('email', 'name', 'phone', 'gender')

		widgets = {
		'email':forms.TextInput(attrs={'placeholder':'Email'}),
		'name':forms.TextInput(attrs={'placeholder':'FullName'})
		}