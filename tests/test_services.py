from datetime import timedelta

from django.test import TestCase
from rest_framework.exceptions import PermissionDenied, ValidationError

from reservations import services
from reservations.exceptions import ConflitMetier
from reservations.models import Reservation
from tests.utils import (
    creer_enseignant,
    creer_gestionnaire,
    creer_salle,
    creneau,
    creneau_passe,
)


class ChevauchementTest(TestCase):
    def setUp(self):
        self.salle = creer_salle()
        self.enseignant = creer_enseignant()
        self.debut, self.fin = creneau(dans_jours=1, heure=9, duree=2)
        self.reference = Reservation.objects.create(
            ressource=self.salle,
            demandeur=self.enseignant,
            debut=self.debut,
            fin=self.fin,
            motif="Cours de reference",
            nombre_participants=10,
            statut=Reservation.Statut.VALIDEE,
        )

    def _conflit(self, decalage_debut_h, duree_h):
        debut = self.debut + timedelta(hours=decalage_debut_h)
        return services.reservations_en_conflit(
            self.salle, debut, debut + timedelta(hours=duree_h)
        ).exists()

    def test_a_fin_a_l_interieur_chevauche(self):
        self.assertTrue(self._conflit(-1, 2))      

    def test_b_debut_a_l_interieur_chevauche(self):
        self.assertTrue(self._conflit(1, 2))       

    def test_c_creneau_inclus_chevauche(self):
        self.assertTrue(self._conflit(0.5, 1))     

    def test_d_creneau_englobant_chevauche(self):
        self.assertTrue(self._conflit(-1, 4))      

    def test_e_creneau_colle_avant_ne_chevauche_pas(self):
        
        self.assertFalse(self._conflit(-2, 2))    

    def test_f_creneau_colle_apres_ne_chevauche_pas(self):
        self.assertFalse(self._conflit(2, 2))     

    def test_une_reservation_en_attente_ne_bloque_pas(self):
        self.reference.statut = Reservation.Statut.EN_ATTENTE
        self.reference.save(update_fields=["statut"])
        self.assertFalse(self._conflit(0, 2))

    def test_une_reservation_annulee_libere_le_creneau(self):
        self.reference.statut = Reservation.Statut.ANNULEE
        self.reference.save(update_fields=["statut"])
        self.assertFalse(self._conflit(0, 2))

    def test_une_autre_ressource_ne_pose_aucun_conflit(self):
        autre_salle = creer_salle(nom="Salle B")
        self.assertFalse(
            services.reservations_en_conflit(
                autre_salle, self.debut, self.fin
            ).exists()
        )


class TransitionsInterditesTest(TestCase):
    def setUp(self):
        self.salle = creer_salle()
        self.enseignant = creer_enseignant()
        self.gestionnaire = creer_gestionnaire()
        self.debut, self.fin = creneau(dans_jours=2)

    def _reservation(self, statut=Reservation.Statut.EN_ATTENTE, passee=False):
        debut, fin = creneau_passe() if passee else (self.debut, self.fin)
        return Reservation.objects.create(
            ressource=self.salle,
            demandeur=self.enseignant,
            debut=debut, fin=fin,
            motif="Test", nombre_participants=5,
            statut=statut,
        )

    def test_valider_une_reservation_deja_validee_leve_409(self):
        reservation = self._reservation(Reservation.Statut.VALIDEE)
        with self.assertRaises(ConflitMetier):
            services.valider(reservation, self.gestionnaire)

    def test_valider_une_reservation_annulee_leve_409(self):
        reservation = self._reservation(Reservation.Statut.ANNULEE)
        with self.assertRaises(ConflitMetier):
            services.valider(reservation, self.gestionnaire)

    def test_refuser_une_reservation_deja_refusee_leve_409(self):
        reservation = self._reservation(Reservation.Statut.REFUSEE)
        with self.assertRaises(ConflitMetier):
            services.refuser(reservation, self.gestionnaire, "Deja traite")

    def test_refuser_sans_commentaire_leve_400(self):
        
        reservation = self._reservation()
        with self.assertRaises(ValidationError):
            services.refuser(reservation, self.gestionnaire, "   ")

    def test_terminer_une_reservation_non_validee_leve_409(self):
        reservation = self._reservation(Reservation.Statut.EN_ATTENTE)
        with self.assertRaises(ConflitMetier):
            services.terminer(reservation, self.gestionnaire)

    def test_terminer_avant_la_fin_du_creneau_leve_409(self):
        reservation = self._reservation(Reservation.Statut.VALIDEE)
        with self.assertRaises(ConflitMetier):
            services.terminer(reservation, self.gestionnaire)

    def test_terminer_une_reservation_passee_fonctionne(self):
        reservation = self._reservation(Reservation.Statut.VALIDEE, passee=True)
        services.terminer(reservation, self.gestionnaire)
        reservation.refresh_from_db()
        self.assertEqual(reservation.statut, Reservation.Statut.TERMINEE)

    def test_un_enseignant_ne_peut_pas_annuler_la_reservation_d_un_autre(self):
        autre = creer_enseignant("enseignant2")
        reservation = self._reservation()
        with self.assertRaises(PermissionDenied):
            services.annuler(reservation, autre)

    def test_valider_libere_puis_bloque_le_creneau(self):
        premiere = self._reservation()
        seconde = self._reservation()

        services.valider(premiere, self.gestionnaire)
        premiere.refresh_from_db()
        self.assertEqual(premiere.statut, Reservation.Statut.VALIDEE)

        with self.assertRaises(ConflitMetier):
            services.valider(seconde, self.gestionnaire)
        seconde.refresh_from_db()
        self.assertEqual(seconde.statut, Reservation.Statut.EN_ATTENTE)
