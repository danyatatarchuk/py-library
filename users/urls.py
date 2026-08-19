from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import MyTokenObtainPairView, UserCreateView, UserMeView


urlpatterns = [
    path("", UserCreateView.as_view(), name="user-create"),
    path("me/", UserMeView.as_view(), name="user-me"),
    path("token/", MyTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]
