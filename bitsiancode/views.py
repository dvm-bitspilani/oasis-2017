from django.shortcuts import render
from ems.models import Bitsian
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from google.oauth2 import id_token
from google.auth.transport import requests
from oasis2017.keyconfig import OAUTH_CLIENT_ID
from django.views.decorators.csrf import csrf_exempt
import json
from api.serializers import BitsianSerializer, AttendanceSerializer
from events.models import *

@csrf_exempt
def index(request):
    token = request.POST['id_token']
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), OAUTH_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return JsonResponse({'message':'Invalid user'})
        email = idinfo['email']
        try:
            bitsian = Bitsian.objects.filter(email=email)[0]
            qr = generate_qr_code(bitsian.barcode)
            response = HttpResponse(content_type="image/jpeg")
            qr.save(response, "JPEG")
            return response
        except:
            return JsonResponse({'message':'Bitsian does not exist.'})
    except:
        return JsonResponse({'message':'Invalid Access.'})

@csrf_exempt
def get_barcode(request):
    token = request.POST['id_token']
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), OAUTH_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return JsonResponse({'message':'Invalid user'})
        email = idinfo['email']
        try:
            bitsian = Bitsian.objects.filter(email=email)[0]
            bitsian_serializer = BitsianSerializer(bitsian)
            profshow_serializer = AttendanceSerializer(Attendance.objects.filter(bitsian=bitsian), many=True)
            return JsonResponse({'bitsian':bitsian_serializer.data, 'prof_shows':profshow_serializer.data})
        except:
            return JsonResponse({'message':'Bitsian does not exist.'})
    except:
        return JsonResponse({'message':'Invalid Access.'})


def generate_qr_code(data):
    import qrcode
    from PIL import Image
    part_code = qrcode.make(data)
    return part_code