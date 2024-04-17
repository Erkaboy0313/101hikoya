import phonenumbers
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

def validate_phone(value):
    try:
        phone = phonenumbers.parse('+' + value)
        if phonenumbers.is_valid_number(phone):
            return value
    except phonenumbers.phonenumberutil.NumberParseException:
        raise serializers.ValidationError(_("Telefon raqami formati xato"))