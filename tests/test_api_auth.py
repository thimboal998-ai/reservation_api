from rest_framework import status
from rest_framework.test import APITestCase

from tests.utils import creer_enseignant

URL_LOGIN = "/api/v1/auth/login/"
URL_PROTEGEE = "/api/v1/reservations/"


class AuthentificationJWTTest(APITestCase):

    def setUp(self):
        self.enseignant = creer_enseignant("prof.ndiaye")
        self.mot_de_passe = "MotDePasseTest123!"

    def test_mauvais_mot_de_passe_retourne_401(self):
        reponse = self.client.post(
            URL_LOGIN,
            {"username": self.enseignant.username, "password": "faux"},
            format="json",
        )
        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_connexion_retourne_les_deux_jetons_et_le_role(self):
        reponse = self.client.post(
            URL_LOGIN,
            {"username": self.enseignant.username, "password": self.mot_de_passe},
            format="json",
        )
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.assertIn("access", reponse.data)
        self.assertIn("refresh", reponse.data)

        self.assertEqual(reponse.data["role"], "enseignant")

    def test_le_jeton_ouvre_une_route_protegee(self):
        acces = self.client.post(
            URL_LOGIN,
            {"username": self.enseignant.username, "password": self.mot_de_passe},
            format="json",
        ).data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {acces}")
        reponse = self.client.get(URL_PROTEGEE)
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)

    def test_un_jeton_invalide_est_rejete(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer jeton.completement.faux")
        reponse = self.client.get(URL_PROTEGEE)
        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)


class SanteTest(APITestCase):

    def test_health_est_public_et_repond_ok(self):
        reponse = self.client.get("/health/")
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.assertEqual(reponse.data["status"], "ok")
        self.assertEqual(reponse.data["database"], "up")
