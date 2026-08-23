
from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    """Un compte de l'application, porteur d'un role metier."""

    class Role(models.TextChoices):
        ENSEIGNANT = "enseignant", "Enseignant"
        GESTIONNAIRE = "gestionnaire", "Gestionnaire"
        ADMINISTRATEUR = "administrateur", "Administrateur"

    role = models.CharField(
        "role metier",
        max_length=20,
        choices=Role.choices,
        default=Role.ENSEIGNANT,
        help_text="Determine ce que le compte a le droit de faire dans l'API.",
    )

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"
        ordering = ["username"]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def est_enseignant(self) -> bool:
        return self.role == self.Role.ENSEIGNANT

    @property
    def est_gestionnaire(self) -> bool:
        return self.role == self.Role.GESTIONNAIRE

    @property
    def est_administrateur(self) -> bool:
        return self.role == self.Role.ADMINISTRATEUR or self.is_superuser

    @property
    def peut_arbitrer(self) -> bool:
        
        return self.est_gestionnaire or self.est_administrateur
