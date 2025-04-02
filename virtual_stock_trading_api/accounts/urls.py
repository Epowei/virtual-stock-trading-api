from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterView, UserDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='api_token_auth'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
]