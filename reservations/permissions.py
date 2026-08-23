from rest_framework.permissions import BasePermission


class EstProprietaireOuGestionnaire(BasePermission):

    message = "Cette reservation ne vous appartient pas."

    def has_object_permission(self, request, view, obj):
        utilisateur = request.user
        if utilisateur.peut_arbitrer:
            return True
        return obj.demandeur_id == utilisateur.id
