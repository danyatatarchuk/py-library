from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import UserCreateView, MyTokenObtainPairView


urlpatterns = [
    path("", UserCreateView.as_view(), name="user-create"),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
