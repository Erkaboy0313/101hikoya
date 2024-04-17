from rest_framework import viewsets,status,response
from .models import CustomUser
from rest_framework.decorators import action
from .serializers import RegistrationSerializer,LoginSerializer,GoogleSocialAuthSerializer
from rest_framework.exceptions import ValidationError
from utils.exception import BaseAPIException
from django.db import transaction
from django.utils.decorators import method_decorator
from .models import CustomUser


@method_decorator(transaction.non_atomic_requests, name='dispatch')
class AuthViewSet(viewsets.ViewSet):
    queryset = CustomUser.objects.all()


    @action(methods=['post'], detail=False)
    def register(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({'foydalanuvchi royxatdan otdi'},status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def login(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.save()
        except ValidationError:
            raise
        except BaseAPIException:
            raise

        return response.Response(data,status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def logout(self, request, *args, **kwargs):
        request.auth.delete()
        return response.Response({'message':'log out'})
    
class GoogleSocialAuthView(viewsets.ViewSet):
    queryset = CustomUser.objects.all()

    def create(self, request):
        serializer = GoogleSocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return response.Response(data, status=status.HTTP_200_OK)