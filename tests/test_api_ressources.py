from rest_framework import status
from rest_framework.test import APITestCase

from ressources.models import Indisponibilite, Ressource
from tests.utils import (
    creer_administrateur,
    creer_enseignant,
    creer_gestionnaire,
    creer_salle,
    creneau,
)

URL_RESSOURCES = "/api/v1/ressources/"
URL_INDISPOS = "/api/v1/indisponibilites/"


class RessourcesTest(APITestCase):

    def setUp(self):
        self.enseignant = creer_enseignant()
        self.gestionnaire = creer_gestionnaire()
        self.admin = creer_administrateur()
        self.salle = creer_salle("Labo systeme", capacite=24)

    def test_un_enseignant_consulte_le_catalogue(self):
        self.client.force_authenticate(self.enseignant)
        reponse = self.client.get(URL_RESSOURCES)
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.assertEqual(reponse.data["count"], 1)

    def test_un_enseignant_ne_cree_pas_de_ressource(self):
        self.client.force_authenticate(self.enseignant)
        reponse = self.client.post(
            URL_RESSOURCES,
            {"nom": "Salle pirate", "type": "salle", "capacite": 10},
            format="json",
        )
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Ressource.objects.count(), 1)

    def test_un_administrateur_cree_une_ressource(self):
        self.client.force_authenticate(self.admin)
        reponse = self.client.post(
            URL_RESSOURCES,
            {"nom": "Salle multimedia", "type": "salle", "capacite": 30},
            format="json",
        )
        self.assertEqual(reponse.status_code, status.HTTP_201_CREATED, reponse.data)
        self.assertEqual(Ressource.objects.count(), 2)

    def test_une_salle_sans_capacite_est_refusee(self):
        """Coherence type/capacite verifiee par RessourceSerializer."""
        self.client.force_authenticate(self.admin)
        reponse = self.client.post(
            URL_RESSOURCES, {"nom": "Salle floue", "type": "salle"}, format="json"
        )
        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("capacite", reponse.data)

    def test_desactiver_une_ressource_par_patch(self):
        """Retirer une salle du parc = active=False, jamais DELETE."""
        self.client.force_authenticate(self.admin)
        reponse = self.client.patch(
            f"{URL_RESSOURCES}{self.salle.id}/", {"active": False}, format="json"
        )
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.salle.refresh_from_db()
        self.assertFalse(self.salle.active)

    def test_delete_non_expose(self):
        self.client.force_authenticate(self.admin)
        reponse = self.client.delete(f"{URL_RESSOURCES}{self.salle.id}/")
        self.assertEqual(reponse.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_filtrage_par_type(self):
        self.client.force_authenticate(self.enseignant)
        reponse = self.client.get(f"{URL_RESSOURCES}?type=equipement")
        self.assertEqual(reponse.data["count"], 0)


class IndisponibilitesTest(APITestCase):

    def setUp(self):
        self.enseignant = creer_enseignant()
        self.gestionnaire = creer_gestionnaire()
        self.salle = creer_salle()
        self.debut, self.fin = creneau(dans_jours=3)

    def _corps(self, **remplacements):
        corps = {
            "ressource": self.salle.id,
            "debut": self.debut.isoformat(),
            "fin": self.fin.isoformat(),
            "motif": "Maintenance electrique",
        }
        corps.update(remplacements)
        return corps

    def test_un_enseignant_ne_declare_pas_d_indisponibilite(self):
        self.client.force_authenticate(self.enseignant)
        reponse = self.client.post(URL_INDISPOS, self._corps(), format="json")
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)

    def test_un_gestionnaire_declare_une_indisponibilite(self):
        self.client.force_authenticate(self.gestionnaire)
        reponse = self.client.post(URL_INDISPOS, self._corps(), format="json")
        self.assertEqual(reponse.status_code, status.HTTP_201_CREATED, reponse.data)
        self.assertEqual(Indisponibilite.objects.count(), 1)

    def test_dates_incoherentes_refusees(self):
        self.client.force_authenticate(self.gestionnaire)
        reponse = self.client.post(
            URL_INDISPOS,
            self._corps(debut=self.fin.isoformat(), fin=self.debut.isoformat()),
            format="json",
        )
        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)

    def test_un_enseignant_consulte_les_indisponibilites(self):
        Indisponibilite.objects.create(
            ressource=self.salle, debut=self.debut, fin=self.fin, motif="Travaux"
        )
        self.client.force_authenticate(self.enseignant)
        reponse = self.client.get(URL_INDISPOS)
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.assertEqual(reponse.data["count"], 1)
