from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from ressources.models import Ressource

Utilisateur = get_user_model()

def creer_utilisateur(username, role=Utilisateur.Role.ENSEIGNANT, **extra):
    return Utilisateur.objects.create_user(
        username=username,
        password="MotDePasseTest123!",
        role=role,
        **extra,
    )


def creer_enseignant(username="enseignant1"):
    return creer_utilisateur(username, Utilisateur.Role.ENSEIGNANT)


def creer_gestionnaire(username="gestionnaire1"):
    return creer_utilisateur(username, Utilisateur.Role.GESTIONNAIRE)


def creer_administrateur(username="admin1"):
    return creer_utilisateur(
        username, Utilisateur.Role.ADMINISTRATEUR, is_staff=True
    )


def creer_salle(nom="Labo reseau", capacite=20, active=True):
    return Ressource.objects.create(
        nom=nom,
        type=Ressource.TypeRessource.SALLE,
        capacite=capacite,
        active=active,
    )


def creer_equipement(nom="Videoprojecteur 1", active=True):
    return Ressource.objects.create(
        nom=nom,
        type=Ressource.TypeRessource.EQUIPEMENT,
        capacite=None,
        active=active,
    )


def creneau(dans_jours=1, heure=9, duree=2):
    base = timezone.now() + timedelta(days=dans_jours)
    debut = base.replace(hour=heure, minute=0, second=0, microsecond=0)
    return debut, debut + timedelta(hours=duree)


def creneau_passe(depuis_jours=2, duree=2):
    debut = timezone.now() - timedelta(days=depuis_jours)
    return debut, debut + timedelta(hours=duree)
