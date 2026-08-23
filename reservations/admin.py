from django.contrib import admin

from reservations.models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("ressource", "demandeur", "debut", "fin", "statut")
    list_filter = ("statut", "ressource")
    search_fields = ("motif", "demandeur__username")
    date_hierarchy = "debut"
   
    readonly_fields = ("statut", "decideur", "decide_le", "cree_le", "modifie_le")
