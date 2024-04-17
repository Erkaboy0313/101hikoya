from rest_framework.authtoken.models import Token
from utils.exception import BaseAPIException
from rest_framework import serializers
from .models import CustomUser
from utils.validators import validate_phone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from .google import Google
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from .register import register_social_user

class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)
    username = serializers.CharField(required=True)
    phone = serializers.CharField(validators=[validate_phone])

    class Meta:
        model = CustomUser
        fields = ['email', 'password','username', 'first_name','last_name', 'phone','birth_date','gender']

    def create(self, validated_data):
        if CustomUser.objects.exist_user(validated_data):
            raise BaseAPIException(_("Foydalanuvchi ro'yxatdan o'tgan"))

        validated_data['password'] = make_password(validated_data['password'])

        self.instance = super().create(validated_data)

        return self.instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(validators=[validate_password])

    class Meta:
        fields = ['username', 'password']

    def save(self, **kwargs):
        data = self.validated_data
        try:
            user: CustomUser = CustomUser.objects.get(username=data['username'])
            if not check_password(data['password'], user.password):
                raise BaseAPIException
        except BaseException:
            raise BaseAPIException(_("Noto'g'ri login yoki parol"))

        token, __ = Token.objects.get_or_create(user=user)
        return {'token': token.key}




class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )
        if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed('oops, who are you?')
        print(user_data)
        user_id = user_data['sub']
        email = user_data['email']
        first_name = user_data['given_name']
        last_name = user_data['family_name']
        name = user_data['name']
        provider = 'google'
        return register_social_user(
            provider=provider, user_id=user_id, email=email, name=name, first_name=first_name, last_name=last_name)



