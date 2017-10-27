from rest_framework import serializers
from events.models import *
from registrations.models import *
from django.contrib.auth.models import User
from ems.models import *

class ParticipantSerializer(serializers.ModelSerializer):
	college_name = serializers.ReadOnlyField(source='college.name', read_only=True)
	class Meta:
		model = Participant
		fields = ('name', 'college_name', 'email', 'city', 'state', 'phone', 'gender', 'year_of_study', 'head_of_society', 'barcode', 'id')

class EventSerializer(serializers.ModelSerializer):

	class Meta:
		model = Event
		fields = ('id', 'name', 'date', 'time','venue', 'appcontent')

class ProfShowSerializer(serializers.ModelSerializer):

	class Meta:
		model = ProfShow
		fields = ('id', 'name', 'price', 'date', 'time' ,'venue', 'appcontent')

class ProfileSerializer(serializers.ModelSerializer):
	pic_url = serializers.SerializerMethodField()
	college_name = serializers.ReadOnlyField(source='college.name', read_only=True)
	class Meta:
		model = Participant
		fields = ('name', 'college_name', 'barcode', 'phone', 'city', 'pcr_approved', 'id', 'paid', 'pic_url')
	
	def get_pic_url(self, participant):
		request = self.context.get('request')
		pic_url = 	participant.profile_pic.url
		return request.build_absolute_uri(pic_url)  # get complete url of profile picture

class AttendanceSerializer(serializers.ModelSerializer):
	
	participant = ParticipantSerializer(required=True, write_only=True)
	prof_show = ProfShowSerializer(required=True, write_only=True)
	prof_show_name = serializers.ReadOnlyField(source='prof_show.name', read_only=True)
	class Meta:
		model = Attendance
		fields = ('id', 'participant', 'prof_show', 'count', 'passed_count', 'prof_show_name')

class BaseEventSerializer(serializers.ModelSerializer):
	category_name = serializers.ReadOnlyField(source='category.name', read_only=True)
	class Meta:
		model = Event
		fields = ('id', 'name', 'category_name')

class EventDetailSerializer(serializers.ModelSerializer):
	category_name = serializers.ReadOnlyField(source='category.name', read_only=True)
	class Meta:
		model = Event
		fields = ('id', 'name', 'content', 'rules','category_name', 'detail_rules','contact')

class ParticipationSerializer(serializers.ModelSerializer):
	
	participant = ParticipantSerializer(required=True, write_only=True)
	event = EventSerializer(required=True, write_only=True)
	class Meta:
		model = Participation
		fields = ('participant', 'event', 'id')

class BitsianSerializer(serializers.ModelSerializer):
	class Meta:
		model = Bitsian
		fields = '__all__'