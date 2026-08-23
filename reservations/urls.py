from rest_framework.routers import DefaultRouter

from reservations.views import ReservationViewSet

router = DefaultRouter()
router.register("reservations", ReservationViewSet, basename="reservation")

urlpatterns = router.urls
