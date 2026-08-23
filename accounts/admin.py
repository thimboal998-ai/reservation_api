
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")

    fieldsets = UserAdmin.fieldsets + (
        ("Role metier", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role metier", {"fields": ("role",)}),
    )
