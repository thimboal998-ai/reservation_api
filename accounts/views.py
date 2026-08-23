
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.serializers import JetonAvecRoleSerializer


class ConnexionView(TokenObtainPairView):

    serializer_class = JetonAvecRoleSerializer
