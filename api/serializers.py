from rest_framework import serializers
from events.models import *
from registrations.models import *
from django.contrib.auth.models import User

class ParticipantSerializer(serializers.ModelSerializer):

    class Meta:
		model = Participant
		fields = ('name', 'college', 'email', 'city', 'state', 'phone', 'gender', 'year_of_study', 'head_of_society', 'barcode', 'id')

class EventSerializer(serializers.ModelSerializer):

	class Meta:
		model = Event
		fields = ('id', 'name', 'min_team_size', 'max_team_size', 'start_date' ,'venue', 'appcontent')

class ProfileSerializer(serializers.ModelSerializer):
	pic_url = serializers.SerializerMethodField()
	class Meta:
		models = Participant
		fields = ('name', 'college', 'barcode', 'phone', 'city', 'pcr_approved', 'id', 'paid', 'pic_url')
	
	def get_pic_url(self, participant):
		request = self.context.get('request')
		pic_url = 	participant.profile_pic.url
		return request.build_absolute_uri(pic_url)  # get complete url of profile picture

class ParticipationSerializer(serializers.ModelSerializer):
	
	participant = ParticipantSerializer(required=True, write_only=True)
	event = EventSerializer(required=True, write_only=True)
	class Meta:
		model = Participation
		fields = '__all__'

class BaseEventSerializer(serializers.ModelSerializer):
	category_name = serializers.ReadOnlyField(source='category.name', read_only=True)
	class Meta:
		model = Event
		fields = ('id', 'name', 'category_name')

class EventDetailSerializer(serializers.ModelSerializer):
	category_name = serializers.ReadOnlyField(source='category.name', read_only=True)
	class Meta:
		model = Event
		fields = ('id', 'name', 'content', 'rules','category_name', 'contact')