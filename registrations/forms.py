from django.contrib.auth.models import User
from django import forms
from .models import *

genders = (

			('M', 'MALE'),
			('F', 'FEMALE'),
		)

class ParticipantForm(forms.ModelForm):
	
	phone = forms.RegexField(regex=r'^\d{10}$')

	class Meta:
		model = Participant
		fields = ('email', 'city', 'name', 'college', 'state', 'phone', 'gender',)

class ImageUploadForm(forms.ModelForm):

	class Meta:
		model = Participant
		fields = ('profile_pic',)

class DocUploadForm(forms.ModelForm):

	class Meta:
		model = Participant
		fields = ('verify_docs',)