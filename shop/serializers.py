from rest_framework import serializers
from registrations.models import *
from shop.models import *
from django.contrib.auth.models import User
import datetime
from pytz import timezone
from events.models import *
class UserSerializer(serializers.ModelSerializer):

	class Meta:
		model = User
		fields = ('id', 'username', 'email')


class CollegeSerializer(serializers.ModelSerializer):
	class Meta:
		model = College
		fields = ('name', 'id')


class ParticipantSerializer(serializers.ModelSerializer):
	college_name = serializers.ReadOnlyField(source='college.name', read_only=True)
	class Meta:
		model = Participant
		fields = ('name', 'college_name', 'email', 'city', 'state', 'phone', 'gender', 'barcode', 'id',)

class ProfShowSerializer(serializers.ModelSerializer):

	class Meta:
		model = ProfShow
		fields = ('id', 'name', 'price', 'date', 'time' ,'venue', 'appcontent')

class ProfileSerializer(serializers.ModelSerializer):
	# pic_url = serializers.SerializerMethodField()
	college_name = serializers.ReadOnlyField(source='college.name', read_only=True)
	class Meta:
		model = Participant
		fields = ('name', 'college_name', 'barcode', 'phone', 'city', 'pcr_approved', 'id', 'paid')
	
	# def get_pic_url(self, participant):
	# 	request = self.context.get('request')
	# 	pic_url = 	participant.profile_pic.url
	# 	return request.build_absolute_uri(pic_url)  # get complete url of profile picture

class AttendanceSerializer(serializers.ModelSerializer):
	
	participant = ParticipantSerializer(required=True, write_only=True)
	prof_show = ProfShowSerializer(required=True, write_only=True)
	prof_show_name = serializers.ReadOnlyField(source='prof_show.name', read_only=True)
	class Meta:
		model = Attendance
		fields = ('id', 'participant', 'prof_show', 'count', 'passed_count', 'prof_show_name', 'number')

class EventDetailSerializer(serializers.ModelSerializer):
	category_name = serializers.ReadOnlyField(source='category.name', read_only=True)
	class Meta:
		model = Event
		fields = ('id', 'name', 'content', 'rules','category_name', 'detail_rules','contact', 'order', 'detail_rules', 'content_rich')

class CategorySerializer(serializers.ModelSerializer):
	events = EventDetailSerializer(required=True, write_only=True, many=True)
	class Meta:
		model = Category
		fields = ('name', 'id', 'order', 'events')

class BitsianSerializer(serializers.ModelSerializer):
	class Meta:
		model = Bitsian	
		fields = '__all__'


class BaseEventSerializer(serializers.ModelSerializer):
	category_name = serializers.ReadOnlyField(source='category.name', read_only=True)
	class Meta:
		model = Event
		fields = ('id', 'name', 'category_name', 'content', 'order', 'content_rich', 'detail_rules')
		
class EventSerializer(serializers.ModelSerializer):

	class Meta:
		model = Event
		fields = ('id', 'name', 'date', 'time','venue', 'appcontent', 'order', 'content')

class ProductMainSerializer(serializers.ModelSerializer):
	name = serializers.SerializerMethodField()
	size = serializers.SerializerMethodField()
	p_type = serializers.SerializerMethodField()
	colour = serializers.SerializerMethodField()
	price = serializers.SerializerMethodField()
	category = serializers.SerializerMethodField()
	categoryid = serializers.SerializerMethodField()

	def get_name(self, obj):
		a_name = obj.product.name
		if not obj.size.name == 'NA':
			a_name += (' ' + obj.size.name)
		if not obj.product.colour.name == 'NA':
			a_name += (' ' + obj.product.colour.name)
		if not obj.product.if_veg is None:
			is_veg = obj.product.if_veg
			if is_veg:
				a_name += "(Veg)"
			else:
				a_name += "(NonVeg)"
		return a_name
	
	def get_size(self,obj):
		return obj.size.name

	def get_p_type(self, obj):
		return obj.product.p_type.name

	def get_colour(self, obj):
		return obj.product.colour.name

	def get_price(self, obj):
		return int(obj.price*(100-obj.discount)/100)

	def get_categoryid(self,obj):
		return obj.product.category.id

	def get_category(self,obj):
		return obj.product.category.name

	class Meta:
		model = ProductMain
		fields = ('id',  'price', 'is_available', 'name', 'size', 'colour', 'p_type', 'category', 'categoryid')


class ProductSerializer(serializers.ModelSerializer):

	mainproducts = ProductMainSerializer(read_only=True, many=True)
	p_type = serializers.SerializerMethodField()
	colour = serializers.SerializerMethodField()

	def get_p_type(self, obj):
		return obj.p_type.name

	def get_colour(self, obj):
		return obj.colour.name

	class Meta:
		model = Product
		fields = ('id', 'name', 'description', 'if_veg', 'mainproducts', 'p_type', 'colour')


class SaleSerializer(serializers.ModelSerializer):
	product = ProductMainSerializer(read_only=True)
	class Meta:
		model = Sale
		fields = ('product', 'quantity', 'id', 'paid')


class StallSerializer(serializers.ModelSerializer):
	
	menu = ProductSerializer(many=True, read_only=True)
	class Meta:
		model = Stall
		fields = ('name', 'id', 'description', 'menu')


class StallSerializerManager(serializers.ModelSerializer):

	menu = ProductMainSerializer(many=True, read_only=True)
	sales = SaleSerializer(many=True, read_only=True)

	class Meta:
		model = Stall
		fields = ('sales', 'menu', 'name', 'id', 'description')

class StallGroupSerializer(serializers.ModelSerializer):
	bitsian = BitsianSerializer(read_only=True)
	participant = ParticipantSerializer(read_only=True)
	sales = SaleSerializer(many=True, read_only=True)
	stallname = serializers.SerializerMethodField()

	def get_stallname(self, obj):
		return obj.stall.name

	created_at = serializers.SerializerMethodField()
	def get_created_at(self, obj):
		return datetime.datetime.strftime(obj.created_at.astimezone(timezone('Asia/Kolkata')), "%d %b %I:%M %p")
		return str(obj.created_at)

	class Meta:
		model = StallGroup
		fields = ('unique_code', 'id', 'created_at', 'bitsian', 'participant', 'order_complete', 'cancelled', 'is_bitsian', 'sales', 'stallname', 'orderid', 'order_ready', 'order_no')

class StallGroupBitsianSerializer(serializers.ModelSerializer):

	bitsian = BitsianSerializer(read_only=True)
	sales = SaleSerializer(many=True, read_only=True)

	class Meta:
		model = StallGroup
		fields = ('sales', 'unique_code', 'bitsian', 'id','order_complete', 'cancelled', 'orderid')

class StallGroupParticipantSerializer(serializers.ModelSerializer):

	participant = ParticipantSerializer(read_only=True)
	sales = SaleSerializer(many=True, read_only=True)

	class Meta:
		model = StallGroup
		fields = ('sales', 'unique_code', 'participant', 'id','order_complete','cancelled', 'orderid')

class CartSerializer(serializers.ModelSerializer):

	sales = SaleSerializer(many=True, read_only=True)
	class Meta:
		model = Cart
		fields = ('created_at', 'amount', 'is_complete', 'sales')


class WalletSerializer(serializers.ModelSerializer):

	user = UserSerializer(read_only=True)
	participant = ParticipantSerializer(read_only=True)
	bitsian = BitsianSerializer(read_only=True)
	spent = serializers.SerializerMethodField()

	def get_spent(self, obj):
		total = 0
		for i in obj.transactions.filter(t_type='buy'):
			if not i.stallgroup.cancelled:
				total += i.value
		return total
	class Meta:
		model = Wallet
		fields = ('phone', 'curr_balance', 'user', 'uid', 'bitsian', 'participant', 'is_bitsian', 'spent', 'userid')


class TransactionSerializer(serializers.ModelSerializer):

	stallgroup = StallGroupSerializer(read_only=True)
	transfer_to_from = WalletSerializer(read_only=True)

	created_at = serializers.SerializerMethodField()
	def get_created_at(self, obj):
		return datetime.datetime.strftime(obj.created_at.astimezone(timezone('Asia/Kolkata')), "%d %b %I:%M %p")

	class Meta:
		model = Transaction
		fields = ('id', 'value', 'created_at', 't_type', 'stallgroup', 'transfer_to_from')


class UserSerializer(serializers.ModelSerializer):

	class Meta:
		model=User
		fields = ('username')

class ParticipationSerializer(serializers.ModelSerializer):
	
	participant = ParticipantSerializer(required=True, write_only=True)
	event = EventSerializer(required=True, write_only=True)
	class Meta:
		model = Participation
		fields = ('participant', 'event', 'id')