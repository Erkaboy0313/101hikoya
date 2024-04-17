from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
import random

User = get_user_model()

def generate_username(name):
    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)


def register_social_user(provider, user_id, email, name, first_name, last_name):
    email_check = User.objects.filter(email=email).first()
    if email_check is not None:
        registered_user = authenticate(
            username=email_check.username, password=user_id)
        if registered_user:

            token, __ = Token.objects.get_or_create(user=registered_user)
            return {'token': token.key}
        
        else:
            raise AuthenticationFailed(
                detail='Your data is not match to login using ' + provider)
    else:
        user = {
            'username': generate_username(name), 'email': email,
            'first_name': first_name, 'last_name': last_name,
            'password': make_password(user_id)
            }
        
        user = User.objects.create(**user)
        new_user = authenticate(
            username=user.username, password=user_id)
        if new_user:

            token, __ = Token.objects.get_or_create(user=user)
            return {'token': token.key}
        
        else:
            raise AuthenticationFailed(
                detail='Please login again.')
