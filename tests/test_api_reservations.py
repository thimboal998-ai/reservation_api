from rest_framework import status
from rest_framework.test import APITestCase

from reservations.models import Reservation
from tests.utils import (
    creer_administrateur,
    creer_enseignant,
    creer_gestionnaire,
    creer_salle,
    creneau,
    creneau_passe,
)

URL_LISTE = "/api/v1/reservations/"


class BaseReservationTest(APITestCase):

    def setUp(self):
        self.enseignant = creer_enseignant("prof.martin")
        self.autre_enseignant = creer_enseignant("prof.diallo")
        self.gestionnaire = creer_gestionnaire("gest.sow")
        self.admin = creer_administrateur("admin.ba")
        self.salle = creer_salle("Labo reseau", capacite=20)
        self.debut, self.fin = creneau(dans_jours=1, heure=9, duree=2)

    def corps_valide(self, **remplacements):
        corps = {
            "ressource": self.salle.id,
            "debut": self.debut.isoformat(),
            "fin": self.fin.isoformat(),
            "motif": "TP routage",
            "nombre_participants": 15,
        }
        corps.update(remplacements)
        return corps

    def creer_reservation(self, demandeur=None, statut=Reservation.Statut.EN_ATTENTE,
                          passee=False, **extra):
        debut, fin = creneau_passe() if passee else (self.debut, self.fin)
        return Reservation.objects.create(
            ressource=extra.pop("ressource", self.salle),
            demandeur=demandeur or self.enseignant,
            debut=debut, fin=fin,
            motif="Reservation de test",
            nombre_participants=10,
            statut=statut,
            **extra,
        )


class AccesAnonymeTest(BaseReservationTest):

    def test_liste_refusee_sans_authentification(self):
        reponse = self.client.get(URL_LISTE)
        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_creation_refusee_sans_authentification(self):
        reponse = self.client.post(URL_LISTE, self.corps_valide(), format="json")
        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Reservation.objects.count(), 0)


class CreationTest(BaseReservationTest):
    def test_creation_valide_retourne_201(self):
        self.client.force_authenticate(self.enseignant)
        reponse = self.client.post(URL_LISTE, self.corps_valide(), format="json")

        self.assertEqual(reponse.status_code, status.HTTP_201_CREATED, reponse.data)
        
        self.assertEqual(Reservation.objects.count(), 1)
        reservation = Reservation.objects.first()
        self.assertEqual(reservation.statut, Reservation.Statut.EN_ATTENTE)
        self.assertEqual(reservation.demandeur, self.enseignant)

    def test_le_demandeur_est_impose_par_le_jeton(self):
        """Tentative d'usurpation : le corps JSON designe quelqu'un d'autre.

        C'est le test de securite le plus important de la creation.
        perform_create() doit ecraser la valeur envoyee par le client.
        """
        self.client.force_authenticate(self.enseignant)
        corps = self.corps_valide(demandeur=self.autre_enseignant.id)
        self.client.post(URL_LISTE, corps, format="json")

        reservation = Reservation.objects.first()
        self.assertEqual(reservation.demandeur, self.enseignant)

    def test_creation_invalide_retourne_400(self):
        self.client.force_authenticate(self.enseignant)
        # fin avant debut : violation de la regle 1.
        corps = self.corps_valide(fin=self.debut.isoformat(),
                                  debut=self.fin.isoformat())
        reponse = self.client.post(URL_LISTE, corps, format="json")

        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_creation_sur_creneau_deja_valide_est_refusee(self):
        self.creer_reservation(statut=Reservation.Statut.VALIDEE)
        self.client.force_authenticate(self.autre_enseignant)
        reponse = self.client.post(URL_LISTE, self.corps_valide(), format="json")
        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)


class RessourceInexistanteTest(BaseReservationTest):

    def test_consultation_d_une_reservation_inexistante_retourne_404(self):
        self.client.force_authenticate(self.gestionnaire)
        reponse = self.client.get(f"{URL_LISTE}999999/")
        self.assertEqual(reponse.status_code, status.HTTP_404_NOT_FOUND)


class ProprieteDesDonneesTest(BaseReservationTest):
    def setUp(self):
        super().setUp()
        self.ma_reservation = self.creer_reservation(self.enseignant)
        self.reservation_du_voisin = self.creer_reservation(self.autre_enseignant)

    def test_un_enseignant_ne_voit_que_ses_reservations_dans_la_liste(self):
        self.client.force_authenticate(self.enseignant)
        reponse = self.client.get(URL_LISTE)

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        identifiants = [r["id"] for r in reponse.data["results"]]
        self.assertIn(self.ma_reservation.id, identifiants)
        self.assertNotIn(self.reservation_du_voisin.id, identifiants)

    def test_consulter_la_reservation_d_un_autre_retourne_404_et_non_403(self):
        
        self.client.force_authenticate(self.enseignant)
        reponse = self.client.get(f"{URL_LISTE}{self.reservation_du_voisin.id}/")
        self.assertEqual(reponse.status_code, status.HTTP_404_NOT_FOUND)

    def test_un_gestionnaire_voit_toutes_les_reservations(self):
        self.client.force_authenticate(self.gestionnaire)
        reponse = self.client.get(URL_LISTE)
        identifiants = [r["id"] for r in reponse.data["results"]]
        self.assertIn(self.ma_reservation.id, identifiants)
        self.assertIn(self.reservation_du_voisin.id, identifiants)


class RolesTest(BaseReservationTest):
    
    def setUp(self):
        super().setUp()
        self.reservation = self.creer_reservation()

    def test_un_enseignant_ne_peut_pas_valider_403(self):
        self.client.force_authenticate(self.enseignant)
        reponse = self.client.post(f"{URL_LISTE}{self.reservation.id}/valider/")
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.statut, Reservation.Statut.EN_ATTENTE)

    def test_un_gestionnaire_peut_valider_200(self):
        self.client.force_authenticate(self.gestionnaire)
        reponse = self.client.post(f"{URL_LISTE}{self.reservation.id}/valider/")
        self.assertEqual(reponse.status_code, status.HTTP_200_OK, reponse.data)

    def test_un_administrateur_peut_aussi_valider(self):
        self.client.force_authenticate(self.admin)
        reponse = self.client.post(f"{URL_LISTE}{self.reservation.id}/valider/")
        self.assertEqual(reponse.status_code, status.HTTP_200_OK, reponse.data)


class ActionsMetierTest(BaseReservationTest):

    def test_valider_change_le_statut_en_base(self):
        reservation = self.creer_reservation()
        self.client.force_authenticate(self.gestionnaire)

        reponse = self.client.post(f"{URL_LISTE}{reservation.id}/valider/")

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.assertEqual(reponse.data["statut"], "validee")
        reservation.refresh_from_db()
        self.assertEqual(reservation.statut, Reservation.Statut.VALIDEE)
        self.assertEqual(reservation.decideur, self.gestionnaire)
        self.assertIsNotNone(reservation.decide_le)

    def test_valider_un_creneau_deja_pris_retourne_409(self):
        premiere = self.creer_reservation(self.enseignant)
        seconde = self.creer_reservation(self.autre_enseignant)
        self.client.force_authenticate(self.gestionnaire)

        self.client.post(f"{URL_LISTE}{premiere.id}/valider/")
        reponse = self.client.post(f"{URL_LISTE}{seconde.id}/valider/")

        self.assertEqual(reponse.status_code, status.HTTP_409_CONFLICT)
        seconde.refresh_from_db()
        self.assertEqual(seconde.statut, Reservation.Statut.EN_ATTENTE)

    def test_refuser_sans_commentaire_retourne_400(self):
        reservation = self.creer_reservation()
        self.client.force_authenticate(self.gestionnaire)
        reponse = self.client.post(
            f"{URL_LISTE}{reservation.id}/refuser/", {}, format="json"
        )
        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)
        reservation.refresh_from_db()
        self.assertEqual(reservation.statut, Reservation.Statut.EN_ATTENTE)

    def test_refuser_avec_commentaire_enregistre_le_motif(self):
        reservation = self.creer_reservation()
        self.client.force_authenticate(self.gestionnaire)
        reponse = self.client.post(
            f"{URL_LISTE}{reservation.id}/refuser/",
            {"commentaire": "Salle deja mobilisee pour un jury"},
            format="json",
        )
        self.assertEqual(reponse.status_code, status.HTTP_200_OK, reponse.data)
        reservation.refresh_from_db()
        self.assertEqual(reservation.statut, Reservation.Statut.REFUSEE)
        self.assertIn("jury", reservation.commentaire_gestionnaire)

    def test_un_enseignant_annule_sa_propre_reservation(self):
        reservation = self.creer_reservation(self.enseignant)
        self.client.force_authenticate(self.enseignant)
        reponse = self.client.post(f"{URL_LISTE}{reservation.id}/annuler/")

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        reservation.refresh_from_db()
        self.assertEqual(reservation.statut, Reservation.Statut.ANNULEE)

    def test_un_enseignant_ne_peut_pas_annuler_celle_d_un_autre(self):
        reservation = self.creer_reservation(self.autre_enseignant)
        self.client.force_authenticate(self.enseignant)
        reponse = self.client.post(f"{URL_LISTE}{reservation.id}/annuler/")

        self.assertEqual(reponse.status_code, status.HTTP_404_NOT_FOUND)
        reservation.refresh_from_db()
        self.assertEqual(reservation.statut, Reservation.Statut.EN_ATTENTE)

    def test_annuler_liberе_le_creneau_pour_une_autre_validation(self):
        
        premiere = self.creer_reservation(self.enseignant)
        seconde = self.creer_reservation(self.autre_enseignant)
        self.client.force_authenticate(self.gestionnaire)

        self.client.post(f"{URL_LISTE}{premiere.id}/valider/")
        self.client.post(f"{URL_LISTE}{premiere.id}/annuler/")
        reponse = self.client.post(f"{URL_LISTE}{seconde.id}/valider/")

        self.assertEqual(reponse.status_code, status.HTTP_200_OK, reponse.data)


    def test_terminer_une_reservation_passee(self):
        reservation = self.creer_reservation(
            statut=Reservation.Statut.VALIDEE, passee=True
        )
        self.client.force_authenticate(self.gestionnaire)
        reponse = self.client.post(f"{URL_LISTE}{reservation.id}/terminer/")

        self.assertEqual(reponse.status_code, status.HTTP_200_OK, reponse.data)
        reservation.refresh_from_db()
        self.assertEqual(reservation.statut, Reservation.Statut.TERMINEE)

    def test_terminer_une_reservation_future_retourne_409(self):
        reservation = self.creer_reservation(statut=Reservation.Statut.VALIDEE)
        self.client.force_authenticate(self.gestionnaire)
        reponse = self.client.post(f"{URL_LISTE}{reservation.id}/terminer/")
        self.assertEqual(reponse.status_code, status.HTTP_409_CONFLICT)


class MethodesNonExposeesTest(BaseReservationTest):

    def setUp(self):
        super().setUp()
        self.reservation = self.creer_reservation()
        self.client.force_authenticate(self.gestionnaire)

    def test_patch_non_autorise(self):
        reponse = self.client.patch(
            f"{URL_LISTE}{self.reservation.id}/",
            {"statut": "validee"}, format="json",
        )
        self.assertEqual(reponse.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_non_autorise(self):
        reponse = self.client.delete(f"{URL_LISTE}{self.reservation.id}/")
        self.assertEqual(reponse.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
