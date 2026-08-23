
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from config.views import health_check

routes_api_v1 = [
    path("auth/", include("accounts.urls")),
    path("", include("ressources.urls")),
    path("", include("reservations.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),

    path("health/", health_check, name="health"),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    path("api/v1/", include(routes_api_v1)),
]
