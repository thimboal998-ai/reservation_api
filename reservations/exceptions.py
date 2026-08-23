
from rest_framework.exceptions import APIException


class ConflitMetier(APIException):

    status_code = 409
    default_detail = "L'operation est impossible dans l'etat actuel."
    default_code = "conflit"
