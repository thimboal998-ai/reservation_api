from django.conf import settings
from django.db import models

from ressources.models import Ressource


class Reservation(models.Model):

    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        VALIDEE = "validee", "Validee"
        REFUSEE = "refusee", "Refusee"
        ANNULEE = "annulee", "Annulee"
        TERMINEE = "terminee", "Terminee"

    ressource = models.ForeignKey(
        Ressource,
        on_delete=models.PROTECT,      
        related_name="reservations",
        verbose_name="ressource",
    )
    demandeur = models.ForeignKey(
        
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reservations",
        verbose_name="demandeur",
    )
    
    debut = models.DateTimeField("debut")
    fin = models.DateTimeField("fin")
    motif = models.TextField("motif")
    nombre_participants = models.PositiveIntegerField("nombre de participants", default=1)

    statut = models.CharField(
        "statut",
        max_length=20,
        choices=Statut.choices,
        default=Statut.EN_ATTENTE,   
        db_index=True,               
    )
    commentaire_gestionnaire = models.TextField(
        "commentaire du gestionnaire", blank=True,
        help_text="Obligatoire en cas de refus (regle 9).",
    )
    decideur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,   
        null=True, blank=True,
        related_name="decisions_reservations",
        verbose_name="decideur",
    )
    decide_le = models.DateTimeField("date de decision", null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "reservation"
        ordering = ["-debut"]
        indexes = [
            
            models.Index(
                fields=["ressource", "statut", "debut"],
                name="idx_reservation_conflit",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(fin__gt=models.F("debut")),
                name="reservation_fin_apres_debut",
            ),
        ]

    def __str__(self):
        return f"{self.ressource} du {self.debut:%d/%m/%Y %H:%M} ({self.get_statut_display()})"

    @property
    def est_en_attente(self) -> bool:
        return self.statut == self.Statut.EN_ATTENTE

    @property
    def est_validee(self) -> bool:
        return self.statut == self.Statut.VALIDEE

    @property
    def est_finale(self) -> bool:
        """Aucune transition n'est plus possible depuis cet etat."""
        return self.statut in {
            self.Statut.REFUSEE, self.Statut.ANNULEE, self.Statut.TERMINEE,
        }
