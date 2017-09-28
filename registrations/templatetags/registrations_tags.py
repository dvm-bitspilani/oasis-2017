from django import template
register = template.Library()
from django.shortcuts import reverse

@register.inclusion_tag('registrations/qr_code.html', takes_context=True)
def get_qrcode_image(context, text):
    url = reverse('registrations:generate_qr')
    return {'url': url, 'text': text}