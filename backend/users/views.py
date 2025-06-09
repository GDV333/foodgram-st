from rest_framework import viewsets

from .models import User
from .serializers import CustomUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
