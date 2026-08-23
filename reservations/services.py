from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from ressources.models import Indisponibilite
from reservations.exceptions import ConflitMetier
from reservations.models import Reservation



def filtrer_chevauchements(queryset, debut, fin):

    return queryset.filter(debut__lt=fin, fin__gt=debut)


def reservations_en_conflit(ressource, debut, fin, exclure_pk=None):
    
    queryset = Reservation.objects.filter(
        ressource=ressource, statut=Reservation.Statut.VALIDEE
    )
    if exclure_pk is not None:
        
        queryset = queryset.exclude(pk=exclure_pk)
    return filtrer_chevauchements(queryset, debut, fin)


def indisponibilites_en_conflit(ressource, debut, fin):

    queryset = Indisponibilite.objects.filter(ressource=ressource)
    return filtrer_chevauchements(queryset, debut, fin)




def _refuser_si_etat_incorrect(reservation, etats_autorises, operation):
    
    if reservation.statut not in etats_autorises:
        raise ConflitMetier(
            f"Impossible de {operation} une reservation au statut "
            f"'{reservation.get_statut_display()}'."
        )


def valider(reservation, gestionnaire):
   
    with transaction.atomic():
        ressource = (
            type(reservation.ressource).objects
            .select_for_update()
            .get(pk=reservation.ressource_id)
        )

        reservation.refresh_from_db()

        _refuser_si_etat_incorrect(
            reservation, {Reservation.Statut.EN_ATTENTE}, "valider"
        )

        if indisponibilites_en_conflit(
            ressource, reservation.debut, reservation.fin
        ).exists():
            raise ConflitMetier(
                "La ressource est declaree indisponible sur ce creneau."
            )

        conflits = reservations_en_conflit(
            ressource, reservation.debut, reservation.fin,
            exclure_pk=reservation.pk,
        )
        if conflits.exists():
            raise ConflitMetier(
                "Une autre reservation validee occupe deja ce creneau."
            )

        reservation.statut = Reservation.Statut.VALIDEE
        reservation.decideur = gestionnaire
        reservation.decide_le = timezone.now()
       
        reservation.save(
            update_fields=["statut", "decideur", "decide_le", "modifie_le"]
        )
    return reservation


def refuser(reservation, gestionnaire, commentaire):
    
    if not commentaire or not commentaire.strip():
        raise ValidationError(
            {"commentaire_gestionnaire": "Un motif de refus est obligatoire."}
        )

    _refuser_si_etat_incorrect(
        reservation, {Reservation.Statut.EN_ATTENTE}, "refuser"
    )

    reservation.statut = Reservation.Statut.REFUSEE
    reservation.commentaire_gestionnaire = commentaire.strip()
    reservation.decideur = gestionnaire
    reservation.decide_le = timezone.now()
    reservation.save(update_fields=[
        "statut", "commentaire_gestionnaire", "decideur",
        "decide_le", "modifie_le",
    ])
    return reservation


def annuler(reservation, utilisateur):
    
    if not utilisateur.peut_arbitrer and reservation.demandeur_id != utilisateur.id:
        raise PermissionDenied("Vous ne pouvez annuler que vos propres reservations.")

    _refuser_si_etat_incorrect(
        reservation,
        {Reservation.Statut.EN_ATTENTE, Reservation.Statut.VALIDEE},
        "annuler",
    )

    reservation.statut = Reservation.Statut.ANNULEE
    reservation.save(update_fields=["statut", "modifie_le"])
    return reservation


def terminer(reservation, gestionnaire):
    
    _refuser_si_etat_incorrect(
        reservation, {Reservation.Statut.VALIDEE}, "terminer"
    )

    if reservation.fin > timezone.now():
        raise ConflitMetier(
            "Une reservation ne peut etre terminee qu'apres la fin du creneau."
        )

    reservation.statut = Reservation.Statut.TERMINEE
    reservation.decideur = gestionnaire
    reservation.decide_le = timezone.now()
    reservation.save(update_fields=[
        "statut", "decideur", "decide_le", "modifie_le",
    ])
    return reservation
