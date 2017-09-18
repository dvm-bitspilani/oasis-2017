from rest_framework import serializers
from events.models import *
from registrations.models import *
from django.contrib.auth.models import User

class ParticipantSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'college', 'email', 'city', 'state', 'phone', 'gender', 'year_of_study', 'head_of_society', 'barcode', 'id')

class EventSerializer(serializers.ModelSerializer):

	class Meta:
		model = Event
		fields = ('id', 'name', 'min_team_size', 'max_team_size', 'start_date' ,'venue', 'appcontent')