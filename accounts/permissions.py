
from rest_framework.permissions import SAFE_METHODS, BasePermission

class EstAdministrateur(BasePermission):

    message = "Reserve aux administrateurs."

    def has_permission(self, request, view):
        utilisateur = request.user
        return bool(utilisateur.is_authenticated and utilisateur.est_administrateur)


class PeutArbitrer(BasePermission):
    
    message = "Seul un gestionnaire peut arbitrer une reservation."

    def has_permission(self, request, view):
        utilisateur = request.user
        return bool(utilisateur.is_authenticated and utilisateur.peut_arbitrer)


class LectureAuthentifieeEcritureAdministrateur(BasePermission):

    message = "Seul un administrateur peut modifier le parc de ressources."

    def has_permission(self, request, view):
        utilisateur = request.user
        if not utilisateur.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return utilisateur.est_administrateur
