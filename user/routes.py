from rest_framework import routers
from .views import AuthViewSet,GoogleSocialAuthView

router = routers.DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth'),
router.register(r'google-auth', GoogleSocialAuthView, basename='google-auth'),