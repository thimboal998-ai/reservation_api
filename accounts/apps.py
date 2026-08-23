from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Declaration de l'application 'accounts' aupres de Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Comptes et roles"
