# accounts/auth_views.py
from rest_framework_simplejwt.views import TokenObtainPairView

from .auth_serializers import FlexibleTokenObtainPairSerializer


class FlexibleTokenObtainPairView(TokenObtainPairView):
    serializer_class = FlexibleTokenObtainPairSerializer
