from django.utils import timezone
from rest_framework import serializers

from reservations import services
from reservations.models import Reservation
from ressources.models import Ressource
from ressources.serializers import RessourceResumeSerializer


class ReservationLectureSerializer(serializers.ModelSerializer):
    """Ce que l'API RENVOIE. """

    ressource = RessourceResumeSerializer(read_only=True)
    demandeur = serializers.CharField(source="demandeur.username", read_only=True)
    statut_libelle = serializers.CharField(source="get_statut_display", read_only=True)
    duree_heures = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            "id", "ressource", "demandeur", "debut", "fin", "duree_heures",
            "motif", "nombre_participants", "statut", "statut_libelle",
            "commentaire_gestionnaire", "cree_le",
        ]

    def get_duree_heures(self, obj) -> float:
        """Duree du creneau en heures, arrondie au dixieme."""
        secondes = (obj.fin - obj.debut).total_seconds()
        return round(secondes / 3600, 1)


class ReservationCreationSerializer(serializers.ModelSerializer):
    """Ce que l'API ACCEPTE en POST. Severe."""

    class Meta:
        model = Reservation
        fields = ["id", "ressource", "debut", "fin", "motif", "nombre_participants"]
        
    def validate_debut(self, valeur):
        """Regle 2 : une reservation ne peut pas etre creee dans le passe."""
        if valeur < timezone.now():
            raise serializers.ValidationError(
                "Une reservation ne peut pas commencer dans le passe."
            )
        return valeur

    def validate_ressource(self, valeur):
        """Regle 3 : une ressource inactive ne peut pas etre reservee."""
        if not valeur.active:
            raise serializers.ValidationError(
                "Cette ressource est desactivee et ne peut pas etre reservee."
            )
        return valeur

    def validate_nombre_participants(self, valeur):
        if valeur < 1:
            raise serializers.ValidationError(
                "Il faut au moins un participant."
            )
        return valeur



    def validate(self, attrs):
        
        debut = attrs.get("debut")
        fin = attrs.get("fin")
        ressource: Ressource = attrs.get("ressource")
        participants = attrs.get("nombre_participants", 1)

        
        if debut and fin and fin <= debut:
            raise serializers.ValidationError(
                {"fin": "La date de fin doit etre posterieure a la date de debut."}
            )

        if (
            ressource
            and ressource.est_une_salle
            and ressource.capacite is not None
            and participants > ressource.capacite
        ):
            raise serializers.ValidationError({
                "nombre_participants": (
                    f"La capacite de {ressource.nom} est de "
                    f"{ressource.capacite} personnes."
                )
            })

        if ressource and debut and fin:
            if services.indisponibilites_en_conflit(ressource, debut, fin).exists():
                raise serializers.ValidationError({
                    "debut": "La ressource est indisponible sur ce creneau "
                             "(maintenance ou blocage declare)."
                })

            if services.reservations_en_conflit(ressource, debut, fin).exists():
                raise serializers.ValidationError({
                    "debut": "Ce creneau est deja reserve pour cette ressource."
                })

        return attrs


class RefusSerializer(serializers.Serializer):

    commentaire = serializers.CharField(
        required=True, allow_blank=False, max_length=1000,
        help_text="Motif du refus, communique a l'enseignant.",
    )
