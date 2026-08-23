
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from reservations.models import Reservation
from ressources.models import Indisponibilite, Ressource

Utilisateur = get_user_model()

MOT_DE_PASSE_DEMO = "Demo1234!"


class Command(BaseCommand):
    help = "Cree un jeu de donnees de demonstration (comptes, parc, reservations)."

    def handle(self, *args, **options):
        comptes = {}
        for username, role in [
            ("prof.malick", Utilisateur.Role.ENSEIGNANT),
            ("prof.diallo", Utilisateur.Role.ENSEIGNANT),
            ("gest.sow", Utilisateur.Role.GESTIONNAIRE),
            ("admin.alpha", Utilisateur.Role.ADMINISTRATEUR),
        ]:
            compte, cree = Utilisateur.objects.get_or_create(
                username=username,
                defaults={"role": role, "is_staff": role == Utilisateur.Role.ADMINISTRATEUR},
            )
            if cree:
                compte.set_password(MOT_DE_PASSE_DEMO)
                compte.save()
            comptes[username] = compte

        labo, _ = Ressource.objects.get_or_create(
            nom="Laboratoire reseau",
            defaults={"type": Ressource.TypeRessource.SALLE, "capacite": 24,
                      "description": "24 postes, baie de brassage."},
        )
        amphi, _ = Ressource.objects.get_or_create(
            nom="Amphi B",
            defaults={"type": Ressource.TypeRessource.SALLE, "capacite": 120},
        )
        projecteur, _ = Ressource.objects.get_or_create(
            nom="Videoprojecteur portable 1",
            defaults={"type": Ressource.TypeRessource.EQUIPEMENT},
        )
        Ressource.objects.get_or_create(
            nom="Kit reseau (retire du service)",
            defaults={"type": Ressource.TypeRessource.EQUIPEMENT, "active": False},
        )

        demain = (timezone.now() + timedelta(days=1)).replace(
            hour=14, minute=0, second=0, microsecond=0
        )
        Indisponibilite.objects.get_or_create(
            ressource=amphi, debut=demain, fin=demain + timedelta(hours=4),
            defaults={"motif": "Maintenance de la sonorisation"},
        )

        base = (timezone.now() + timedelta(days=2)).replace(
            hour=8, minute=0, second=0, microsecond=0
        )
        scenarios = [
            (labo, "prof.malick", 0, 2, Reservation.Statut.EN_ATTENTE, 20),
            (labo, "prof.diallo", 4, 2, Reservation.Statut.VALIDEE, 18),
            (projecteur, "prof.malick", 0, 3, Reservation.Statut.EN_ATTENTE, 1),
            (amphi, "prof.diallo", 24, 2, Reservation.Statut.EN_ATTENTE, 90),
        ]
        for ressource, auteur, decalage, duree, statut, participants in scenarios:
            debut = base + timedelta(hours=decalage)
            Reservation.objects.get_or_create(
                ressource=ressource,
                demandeur=comptes[auteur],
                debut=debut,
                defaults={
                    "fin": debut + timedelta(hours=duree),
                    "motif": "Seance de travaux pratiques",
                    "nombre_participants": participants,
                    "statut": statut,
                },
            )

        self.stdout.write(self.style.SUCCESS("Jeu de donnees cree."))
        self.stdout.write(f"  Comptes (mot de passe : {MOT_DE_PASSE_DEMO})")
        for username, compte in comptes.items():
            self.stdout.write(f"    - {username:<14} role = {compte.role}")
        self.stdout.write(
            "  Astuce demo : prof.malick depose, gest.sow valide, "
            "puis tentez de valider la demande concurrente -> 409."
        )
