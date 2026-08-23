from django.db import models


class Ressource(models.Model):
    

    class TypeRessource(models.TextChoices):
        SALLE = "salle", "Salle"
        EQUIPEMENT = "equipement", "Equipement"

    nom = models.CharField("nom", max_length=150, unique=True)
    type = models.CharField(
        "type",
        max_length=20,
        choices=TypeRessource.choices,
        default=TypeRessource.SALLE,
    )

    capacite = models.PositiveIntegerField(
        "capacite", null=True, blank=True,
        help_text="Nombre de places. A renseigner pour les salles uniquement.",
    )
    active = models.BooleanField(
        "active", default=True,
        help_text="Une ressource inactive ne peut plus etre reservee (regle 3).",
    )
    description = models.TextField("description", blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ressource"
        ordering = ["nom"]

    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"

    @property
    def est_une_salle(self) -> bool:

        return self.type == self.TypeRessource.SALLE


class Indisponibilite(models.Model):

    ressource = models.ForeignKey(
        Ressource,
        on_delete=models.CASCADE,
        related_name="indisponibilites",
        verbose_name="ressource",
    )
    

    debut = models.DateTimeField("debut")
    fin = models.DateTimeField("fin")
    motif = models.CharField("motif", max_length=255)

    class Meta:
        verbose_name = "indisponibilite"
        verbose_name_plural = "indisponibilites"
        ordering = ["-debut"]
        constraints = [
            
            models.CheckConstraint(
                condition=models.Q(fin__gt=models.F("debut")),
                name="indisponibilite_fin_apres_debut",
            ),
        ]

    def __str__(self):
        return f"{self.ressource.nom} indisponible : {self.motif}"
