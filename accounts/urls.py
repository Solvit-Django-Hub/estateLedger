from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginAPIView, RegisterAPIView, LogoutAPIView, ActivateAccountAPIView, CustomTokenRefreshView, StaffStatusAPIView, StaffCreateAPIView


urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("activate/<str:uidb64>/<str:token>/", ActivateAccountAPIView.as_view(), name="account-activate"),
    path("staff/<int:user_id>/status/", StaffStatusAPIView.as_view(), name="staff-status"),
    path("staff/", StaffCreateAPIView.as_view(), name="staff-create"),

]