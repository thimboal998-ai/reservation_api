from rest_framework import serializers

from ressources.models import Indisponibilite, Ressource


class RessourceSerializer(serializers.ModelSerializer):
    type_libelle = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Ressource
        fields = [
            "id", "nom", "type", "type_libelle",
            "capacite", "active", "description", "cree_le",
        ]
        read_only_fields = ["id", "cree_le"]

    def validate(self, attrs):
        type_ressource = attrs.get(
            "type", getattr(self.instance, "type", None)
        )
        capacite = attrs.get(
            "capacite", getattr(self.instance, "capacite", None)
        )

        if type_ressource == Ressource.TypeRessource.SALLE and capacite is None:
            raise serializers.ValidationError(
                {"capacite": "Une salle doit avoir une capacite."}
            )
        if type_ressource == Ressource.TypeRessource.EQUIPEMENT and capacite:
            raise serializers.ValidationError(
                {"capacite": "Un equipement n'a pas de capacite d'accueil."}
            )
        return attrs


class RessourceResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ressource
        fields = ["id", "nom", "type", "capacite"]


class IndisponibiliteSerializer(serializers.ModelSerializer):

    ressource_nom = serializers.CharField(source="ressource.nom", read_only=True)

    class Meta:
        model = Indisponibilite
        fields = ["id", "ressource", "ressource_nom", "debut", "fin", "motif"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        debut = attrs.get("debut", getattr(self.instance, "debut", None))
        fin = attrs.get("fin", getattr(self.instance, "fin", None))
        if debut and fin and fin <= debut:
            raise serializers.ValidationError(
                {"fin": "La date de fin doit etre posterieure a la date de debut."}
            )
        return attrs
