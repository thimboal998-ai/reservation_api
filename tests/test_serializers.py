from django.test import TestCase

from ressources.models import Indisponibilite
from reservations.serializers import ReservationCreationSerializer
from tests.utils import creer_equipement, creer_salle, creneau


class ReservationValidationTest(TestCase):
    def setUp(self):
        self.salle = creer_salle(capacite=20)
        self.debut, self.fin = creneau(dans_jours=1, heure=9, duree=2)

    def _donnees(self, **remplacements):
        donnees = {
            "ressource": self.salle.id,
            "debut": self.debut,
            "fin": self.fin,
            "motif": "Travaux pratiques reseau",
            "nombre_participants": 15,
        }
        donnees.update(remplacements)
        return donnees


    def test_donnees_valides_sont_acceptees(self):
        serialiseur = ReservationCreationSerializer(data=self._donnees())
        self.assertTrue(serialiseur.is_valid(), serialiseur.errors)

    def test_motif_absent_est_refuse(self):
        donnees = self._donnees()
        del donnees["motif"]
        serialiseur = ReservationCreationSerializer(data=donnees)
        self.assertFalse(serialiseur.is_valid())
        self.assertIn("motif", serialiseur.errors)

    def test_fin_anterieure_au_debut_est_refusee(self):
        serialiseur = ReservationCreationSerializer(
            data=self._donnees(debut=self.fin, fin=self.debut)
        )
        self.assertFalse(serialiseur.is_valid())
        self.assertIn("fin", serialiseur.errors)

    def test_fin_egale_au_debut_est_refusee(self):
        serialiseur = ReservationCreationSerializer(
            data=self._donnees(fin=self.debut)
        )
        self.assertFalse(serialiseur.is_valid())

    def test_reservation_dans_le_passe_est_refusee(self):
        debut, fin = creneau(dans_jours=-3)
        serialiseur = ReservationCreationSerializer(
            data=self._donnees(debut=debut, fin=fin)
        )
        self.assertFalse(serialiseur.is_valid())
        self.assertIn("debut", serialiseur.errors)

    def test_ressource_inactive_est_refusee(self):
        salle_fermee = creer_salle(nom="Salle en travaux", active=False)
        serialiseur = ReservationCreationSerializer(
            data=self._donnees(ressource=salle_fermee.id)
        )
        self.assertFalse(serialiseur.is_valid())
        self.assertIn("ressource", serialiseur.errors)

    def test_capacite_depassee_est_refusee(self):
        serialiseur = ReservationCreationSerializer(
            data=self._donnees(nombre_participants=50)   
        )
        self.assertFalse(serialiseur.is_valid())
        self.assertIn("nombre_participants", serialiseur.errors)

    def test_capacite_exacte_est_acceptee(self):
        serialiseur = ReservationCreationSerializer(
            data=self._donnees(nombre_participants=20)
        )
        self.assertTrue(serialiseur.is_valid(), serialiseur.errors)

    def test_equipement_sans_capacite_accepte_beaucoup_de_participants(self):
        projecteur = creer_equipement()
        serialiseur = ReservationCreationSerializer(
            data=self._donnees(ressource=projecteur.id, nombre_participants=200)
        )
        self.assertTrue(serialiseur.is_valid(), serialiseur.errors)

    def test_creneau_couvert_par_une_indisponibilite_est_refuse(self):
        Indisponibilite.objects.create(
            ressource=self.salle,
            debut=self.debut,
            fin=self.fin,
            motif="Maintenance electrique",
        )
        serialiseur = ReservationCreationSerializer(data=self._donnees())
        self.assertFalse(serialiseur.is_valid())

    def test_indisponibilite_qui_ne_chevauche_pas_laisse_passer(self):
        
        from datetime import timedelta
        Indisponibilite.objects.create(
            ressource=self.salle,
            debut=self.fin + timedelta(hours=1),
            fin=self.fin + timedelta(hours=3),
            motif="Maintenance plus tard dans la journee",
        )
        serialiseur = ReservationCreationSerializer(data=self._donnees())
        self.assertTrue(serialiseur.is_valid(), serialiseur.errors)
