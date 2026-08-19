from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializers import (
    MyTokenObtainPairSerializer,
    UserSerializer,
)


class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
