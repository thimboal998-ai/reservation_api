from django.contrib import admin

from ressources.models import Indisponibilite, Ressource


@admin.register(Ressource)
class RessourceAdmin(admin.ModelAdmin):
    list_display = ("nom", "type", "capacite", "active")
    list_filter = ("type", "active")
    search_fields = ("nom", "description")


@admin.register(Indisponibilite)
class IndisponibiliteAdmin(admin.ModelAdmin):
    list_display = ("ressource", "debut", "fin", "motif")
    list_filter = ("ressource",)
