from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import PeutArbitrer
from reservations import services
from reservations.models import Reservation
from reservations.permissions import EstProprietaireOuGestionnaire
from reservations.serializers import (
    RefusSerializer,
    ReservationCreationSerializer,
    ReservationLectureSerializer,
)


@extend_schema_view(
    
    list=extend_schema(summary="Lister les reservations visibles par l'appelant"),
    create=extend_schema(summary="Deposer une demande de reservation"),
    retrieve=extend_schema(summary="Consulter une reservation"),
)
class ReservationViewSet(
    mixins.ListModelMixin,      
    mixins.CreateModelMixin,   
    mixins.RetrieveModelMixin,  
    viewsets.GenericViewSet,    
):

    
    permission_classes = [IsAuthenticated, EstProprietaireOuGestionnaire]

    def get_serializer_class(self):

        if self.action == "create":
            return ReservationCreationSerializer
        if self.action == "refuser":
            return RefusSerializer
        return ReservationLectureSerializer

 
    def get_queryset(self):
    
        queryset = (
            Reservation.objects
            .select_related("ressource", "demandeur")
        )

        utilisateur = self.request.user
        
        if not utilisateur.is_authenticated:
            return queryset.none()
        if not utilisateur.peut_arbitrer:
            queryset = queryset.filter(demandeur=utilisateur)

        statut = self.request.query_params.get("statut")
        ressource = self.request.query_params.get("ressource")
        if statut:
            queryset = queryset.filter(statut=statut)
        if ressource:
            queryset = queryset.filter(ressource_id=ressource)
        return queryset


    def perform_create(self, serializer):
        serializer.save(demandeur=self.request.user)

    def create(self, request, *args, **kwargs):
       
        serialiseur = self.get_serializer(data=request.data)
        
        serialiseur.is_valid(raise_exception=True)
        self.perform_create(serialiseur)
        lecture = ReservationLectureSerializer(
            serialiseur.instance, context=self.get_serializer_context()
        )
        return Response(lecture.data, status=status.HTTP_201_CREATED)

    def _reponse(self, reservation):
        
        return Response(
            ReservationLectureSerializer(
                reservation, context=self.get_serializer_context()
            ).data
        )

    @extend_schema(
        summary="Valider une reservation en attente",
        request=None,
        description=(
            "Reserve aux gestionnaires. Renvoie 409 si le creneau est "
            "deja occupe par une reservation validee ou couvert par une "
            "indisponibilite."
        ),
    )
    @action(detail=True, methods=["post"], url_path="valider",
            permission_classes=[PeutArbitrer])
    def valider(self, request, pk=None):
        reservation = self.get_object()
        services.valider(reservation, request.user)
        return self._reponse(reservation)

    @extend_schema(
        summary="Refuser une reservation en attente",
        request=RefusSerializer,
        description="Reserve aux gestionnaires. Le commentaire est obligatoire.",
    )
    @action(detail=True, methods=["post"], url_path="refuser",
            permission_classes=[PeutArbitrer])
    def refuser(self, request, pk=None):
        reservation = self.get_object()
        formulaire = RefusSerializer(data=request.data)
        formulaire.is_valid(raise_exception=True)
        services.refuser(
            reservation, request.user, formulaire.validated_data["commentaire"]
        )
        return self._reponse(reservation)

    @extend_schema(summary="Annuler sa propre reservation", request=None)
    @action(detail=True, methods=["post"], url_path="annuler")
    def annuler(self, request, pk=None):
        reservation = self.get_object()
        services.annuler(reservation, request.user)
        return self._reponse(reservation)

    @extend_schema(
        summary="Cloturer une reservation dont le creneau est passe",
        request=None,
    )
    @action(detail=True, methods=["post"], url_path="terminer",
            permission_classes=[PeutArbitrer])
    def terminer(self, request, pk=None):
        reservation = self.get_object()
        services.terminer(reservation, request.user)
        return self._reponse(reservation)
