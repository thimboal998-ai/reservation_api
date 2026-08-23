from rest_framework.routers import DefaultRouter

from ressources.views import IndisponibiliteViewSet, RessourceViewSet

router = DefaultRouter()

router.register("ressources", RessourceViewSet, basename="ressource")
router.register("indisponibilites", IndisponibiliteViewSet, basename="indisponibilite")

urlpatterns = router.urls
