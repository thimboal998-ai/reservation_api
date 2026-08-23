from rest_framework import viewsets

from accounts.permissions import LectureAuthentifieeEcritureAdministrateur
from ressources.models import Indisponibilite, Ressource
from ressources.permissions import LectureTousEcritureGestionnaire
from ressources.serializers import IndisponibiliteSerializer, RessourceSerializer


class RessourceViewSet(viewsets.ModelViewSet):

    queryset = Ressource.objects.all()
    serializer_class = RessourceSerializer
    permission_classes = [LectureAuthentifieeEcritureAdministrateur]

    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        
        queryset = super().get_queryset()
        type_demande = self.request.query_params.get("type")
        actives = self.request.query_params.get("active")
        if type_demande:
            queryset = queryset.filter(type=type_demande)
        if actives is not None:
            queryset = queryset.filter(active=actives.lower() == "true")
        return queryset


class IndisponibiliteViewSet(viewsets.ModelViewSet):

    serializer_class = IndisponibiliteSerializer
    permission_classes = [LectureTousEcritureGestionnaire]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        queryset = Indisponibilite.objects.select_related("ressource")
        ressource = self.request.query_params.get("ressource")
        if ressource:
            queryset = queryset.filter(ressource_id=ressource)
        return queryset
