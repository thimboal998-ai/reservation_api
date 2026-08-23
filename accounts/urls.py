
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from accounts.views import ConnexionView

urlpatterns = [
    path("login/", ConnexionView.as_view(), name="connexion"),
    path("refresh/", TokenRefreshView.as_view(), name="rafraichir"),
    path("verify/", TokenVerifyView.as_view(), name="verifier"),
]
