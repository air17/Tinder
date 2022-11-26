from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import ProfileViewSet, register, set_location

app_name = "api"

router = routers.SimpleRouter()
router.register("users", ProfileViewSet, basename="profile")

urlpatterns = [
    path("register/", register, name="register"),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("set-location/", set_location, name="set-location"),
] + router.urls
