from django.urls import path
from .views import populate

urlpatterns = [
    path('populate/',populate)
]
