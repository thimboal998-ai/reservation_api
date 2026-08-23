from rest_framework.permissions import SAFE_METHODS, BasePermission


class LectureTousEcritureGestionnaire(BasePermission):

    message = "Seul un gestionnaire peut declarer une indisponibilite."

    def has_permission(self, request, view):
        utilisateur = request.user
        if not utilisateur.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return utilisateur.peut_arbitrer
